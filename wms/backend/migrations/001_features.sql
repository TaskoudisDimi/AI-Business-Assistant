-- 001: barcode / supplier / expiry tracking, lots, integrations, alerts, AI usage,
-- and atomic stock functions. Idempotent: safe to run more than once.

-- ── Products ────────────────────────────────────────────────────────────────
alter table products add column if not exists barcode        text;
alter table products add column if not exists supplier       text;
alter table products add column if not exists lead_time_days integer not null default 7;
alter table products add column if not exists track_expiry   boolean not null default false;
create index if not exists products_business_barcode_idx on products (business_id, barcode);

-- ── Lots / expiry ───────────────────────────────────────────────────────────
create table if not exists inventory_lots (
  id          uuid primary key default gen_random_uuid(),
  business_id uuid not null references businesses(id) on delete cascade,
  product_id  uuid not null references products(id) on delete cascade,
  lot_code    text,
  expiry_date date,
  quantity    integer not null default 0 check (quantity >= 0),
  received_at timestamptz not null default now()
);
create index if not exists inventory_lots_product_idx on inventory_lots (product_id, expiry_date);
create index if not exists inventory_lots_business_expiry_idx on inventory_lots (business_id, expiry_date) where quantity > 0;

-- delta = signed change in stock (adjustments store the absolute count in `quantity`)
alter table inventory_movements add column if not exists delta  integer;
alter table inventory_movements add column if not exists lot_id uuid references inventory_lots(id) on delete set null;
create index if not exists inventory_movements_business_created_idx on inventory_movements (business_id, created_at);

alter table order_items add column if not exists lot_code    text;
alter table order_items add column if not exists expiry_date date;

-- ── Alerts ──────────────────────────────────────────────────────────────────
alter table businesses add column if not exists alert_email_enabled boolean not null default true;
alter table businesses add column if not exists alert_last_sent_at  timestamptz;

-- ── E-shop integrations ─────────────────────────────────────────────────────
create table if not exists integrations (
  id            uuid primary key default gen_random_uuid(),
  business_id   uuid not null references businesses(id) on delete cascade,
  provider      text not null check (provider in ('woocommerce', 'shopify')),
  secret        text not null,
  enabled       boolean not null default true,
  last_event_at timestamptz,
  created_at    timestamptz not null default now(),
  unique (business_id, provider)
);

-- One row per processed shop order, so webhook retries don't move stock twice
create table if not exists integration_events (
  id             uuid primary key default gen_random_uuid(),
  integration_id uuid not null references integrations(id) on delete cascade,
  external_id    text not null,
  order_id       uuid references orders(id) on delete set null,
  created_at     timestamptz not null default now(),
  unique (integration_id, external_id)
);

-- ── AI usage (per-business daily limit) ─────────────────────────────────────
create table if not exists ai_requests (
  id          uuid primary key default gen_random_uuid(),
  business_id uuid not null references businesses(id) on delete cascade,
  kind        text not null,
  created_at  timestamptz not null default now()
);
create index if not exists ai_requests_business_created_idx on ai_requests (business_id, created_at);

-- ── Atomic stock changes ────────────────────────────────────────────────────
-- Locks the inventory row so concurrent orders can't overwrite each other's
-- updates. p_absolute sets the count (stock-take / adjustment); otherwise p_delta
-- is added. Stock never goes below zero.
create or replace function wms_adjust_stock(
  p_business uuid, p_product uuid, p_delta integer, p_absolute integer default null
) returns table (old_quantity integer, new_quantity integer)
language plpgsql as $$
declare
  v_old integer;
  v_new integer;
begin
  select quantity into v_old from inventory_items
   where business_id = p_business and product_id = p_product
   for update;
  if not found then
    insert into inventory_items (product_id, business_id, quantity) values (p_product, p_business, 0);
    v_old := 0;
  end if;
  v_new := greatest(coalesce(p_absolute, v_old + p_delta), 0);
  update inventory_items set quantity = v_new, last_updated = now()
   where business_id = p_business and product_id = p_product;
  return query select v_old, v_new;
end $$;

-- Takes p_qty out of a product's lots, earliest expiry first (FEFO).
create or replace function wms_consume_lots(p_product uuid, p_qty integer)
returns void language plpgsql as $$
declare
  r record;
  remaining integer := p_qty;
  take integer;
begin
  for r in
    select id, quantity from inventory_lots
     where product_id = p_product and quantity > 0
     order by expiry_date asc nulls last, received_at asc
     for update
  loop
    exit when remaining <= 0;
    take := least(r.quantity, remaining);
    update inventory_lots set quantity = quantity - take where id = r.id;
    remaining := remaining - take;
  end loop;
end $$;

-- Only the backend (service role) may call these
revoke all on function wms_adjust_stock(uuid, uuid, integer, integer) from public, anon, authenticated;
revoke all on function wms_consume_lots(uuid, integer) from public, anon, authenticated;
grant execute on function wms_adjust_stock(uuid, uuid, integer, integer) to service_role;
grant execute on function wms_consume_lots(uuid, integer) to service_role;
