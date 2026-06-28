# AI Business Assistant

A full-stack business management platform combining warehouse management (WMS), customer analytics with RFM segmentation, and AI-powered sales forecasting.

**Live:** https://wms.task-code.com

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3 + TypeScript + Vite |
| State management | Pinia |
| Routing | Vue Router |
| i18n | vue-i18n (English / Greek) |
| Backend | FastAPI (Python 3.12) |
| Database | Supabase (PostgreSQL) |
| Auth | Supabase Auth — JWT stored in httponly cookies |
| ML | scikit-learn, pandas, numpy (Random Forest) |
| Production server | Hetzner VPS — Traefik v3 reverse proxy + systemd |

---

## Features

### Warehouse Management (WMS)
- **Products** — SKU catalog with reorder points, cost/sell prices, categories
- **Inventory** — Real-time stock levels, movement log (inbound / outbound / adjustment)
- **Orders** — Purchase and sale orders with line items; completing an order automatically updates stock
- **AI Reorder Suggestions** — Calculates days-until-stockout per product based on last 30 days of outbound movements; flags critical and warning items

### Analytics
- **Customer Analysis** — RFM segmentation (High Value, Loyal, At Risk, New, Dormant) derived from completed sale orders; top products by revenue
- **Sales Forecast** — Upload a CSV dataset, run predictions using a pre-trained Random Forest model, view results per day for up to N future days
- **Dashboard** — Live KPIs (revenue, orders, customers, critical stock), recent orders panel, critical stock alerts

### Auth
- Email/password registration with email confirmation
- Secure httponly cookies (access + refresh tokens, 7-day / 30-day TTL)
- Auto-refresh via middleware on every request
- A default business is auto-created for new users on first login

---

## Project Structure

```
AI-Business-Assistant/
├── AI-Buismess-Assitant/          # main app directory
│   ├── backend/
│   │   ├── main.py                # FastAPI app, CORS, middleware, routers, static file serving
│   │   ├── requirements.txt
│   │   ├── models/
│   │   │   └── sales_model.pkl    # pre-trained Random Forest artifact
│   │   ├── api/routes/
│   │   │   ├── auth.py            # /api/auth — login, register, logout, /me
│   │   │   ├── user.py            # /api/users
│   │   │   ├── business.py        # /api/business
│   │   │   ├── products.py        # /api/products — SKU catalog
│   │   │   ├── inventory.py       # /api/inventory — stock, movements, reorder suggestions
│   │   │   ├── orders.py          # /api/orders — purchase & sale orders
│   │   │   ├── customers.py       # /api/customers/analysis — RFM
│   │   │   ├── datasets.py        # /api/datasets — CSV upload to Supabase Storage
│   │   │   └── predictions.py     # /api/predictions — sales forecast
│   │   ├── core/
│   │   │   ├── security.py        # get_current_user() — reads JWT from cookie
│   │   │   ├── middleware.py      # RefreshSessionMiddleware — auto-refresh tokens
│   │   │   ├── config.py
│   │   │   └── exceptions.py
│   │   ├── db/
│   │   │   └── supabase_client.py
│   │   └── services/
│   │       └── permissions.py     # check_business_access()
│   │
│   └── frontend/ui/
│       ├── src/
│       │   ├── views/
│       │   │   ├── Dashboard.vue
│       │   │   ├── CustomerAnalysis.vue
│       │   │   ├── SalesForecast.vue
│       │   │   ├── Datasets.vue
│       │   │   ├── Settings.vue
│       │   │   ├── wms/
│       │   │   │   ├── Products.vue
│       │   │   │   ├── Inventory.vue
│       │   │   │   └── Orders.vue
│       │   │   └── Auth/
│       │   │       ├── Login.vue
│       │   │       └── Register.vue
│       │   ├── components/
│       │   │   ├── Sidebar.vue
│       │   │   ├── Topbar.vue
│       │   │   └── StatCard.vue
│       │   ├── layouts/
│       │   │   ├── AppLayout.vue
│       │   │   └── AuthLayout.vue
│       │   ├── stores/
│       │   │   └── auth.ts        # user + business state (Pinia)
│       │   ├── services/
│       │   │   └── api.ts         # axios instance — baseURL from VITE_API_URL
│       │   ├── router/index.ts
│       │   └── i18n/
│       │       ├── en.json
│       │       └── el.json
│       ├── vite.config.ts
│       └── package.json
└── start.sh                       # dev: starts backend + frontend together
```

---

## Database Schema (Supabase)

Run in the Supabase SQL Editor:

```sql
-- Products / SKU catalog
create table products (
  id            uuid primary key default gen_random_uuid(),
  business_id   uuid not null references businesses(id) on delete cascade,
  sku           text not null,
  name          text not null,
  category      text,
  unit          text default 'τεμ',
  reorder_point integer default 0,
  cost_price    numeric(10,2),
  sell_price    numeric(10,2),
  created_at    timestamptz default now(),
  unique(business_id, sku)
);

-- Current stock levels (one row per product)
create table inventory_items (
  id           uuid primary key default gen_random_uuid(),
  product_id   uuid not null references products(id) on delete cascade,
  business_id  uuid not null,
  quantity     integer not null default 0,
  last_updated timestamptz default now()
);

-- Movement log — immutable audit trail
create table inventory_movements (
  id          uuid primary key default gen_random_uuid(),
  product_id  uuid not null references products(id) on delete cascade,
  business_id uuid not null,
  type        text not null check (type in ('inbound','outbound','adjustment')),
  quantity    integer not null,
  reason      text,
  order_id    uuid,
  created_by  uuid,
  created_at  timestamptz default now()
);

-- Orders (purchase = inbound stock, sale = outbound stock)
create table orders (
  id          uuid primary key default gen_random_uuid(),
  business_id uuid not null references businesses(id) on delete cascade,
  type        text not null check (type in ('purchase','sale')),
  status      text not null default 'draft' check (status in ('draft','confirmed','completed','cancelled')),
  party_name  text,
  notes       text,
  created_by  uuid,
  created_at  timestamptz default now()
);

-- Order line items
create table order_items (
  id         uuid primary key default gen_random_uuid(),
  order_id   uuid not null references orders(id) on delete cascade,
  product_id uuid not null references products(id),
  quantity   integer not null,
  unit_price numeric(10,2)
);
```

---

## Environment Variables

### Backend — `backend/.env`

```env
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=your-service-role-key
COOKIE_SECURE=true          # set to false for local dev (no HTTPS)
SALES_MODEL_PATH=models/sales_model.pkl
```

### Frontend — `frontend/ui/.env.local` (gitignored)

```env
VITE_API_URL=http://localhost:8000/api
```

In production this variable is not set — the frontend defaults to `/api` (same-origin, proxied by Traefik).

---

## Local Development

**Requirements:** Python 3.12, Node 20, a Supabase project

```bash
# 1. Backend
cd AI-Buismess-Assitant/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill in SUPABASE_URL and SUPABASE_KEY
uvicorn main:app --reload --port 8000

# 2. Frontend (separate terminal)
cd AI-Buismess-Assitant/frontend/ui
npm install
# create .env.local with: VITE_API_URL=http://localhost:8000/api
npm run dev
```

Or use the helper script from the root:

```bash
./start.sh
```

Frontend runs on http://localhost:5173, backend on http://localhost:8000.

---

## Production Deployment (Hetzner + Traefik)

The server runs Traefik v3 in Docker as the single entry point for all traffic. The backend runs as a systemd service directly on the host.

### Architecture

```
Browser → wms.task-code.com:443
                │
          [Traefik container]          # owns ports 80 & 443
          reads /opt/taskcode/traefik-conf/wms.yml
                │
          [UFW firewall]               # allows 172.18.0.0/16 → port 8001
                │
          [uvicorn :8001]              # systemd service on host
                │
          [FastAPI]
          ├── /api/...  →  Python routes
          └── /         →  Vue dist/ (index.html + assets)
```

### 1. Build the frontend

```bash
cd AI-Buismess-Assitant/frontend/ui
npm run build-only        # outputs to dist/
```

### 2. systemd service — `/etc/systemd/system/wms-backend.service`

```ini
[Unit]
Description=WMS Backend
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/AI-Business-Assistant/AI-Buismess-Assitant/backend
ExecStart=/var/www/AI-Business-Assistant/AI-Buismess-Assitant/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable --now wms-backend
```

### 3. Traefik config — `/opt/taskcode/traefik-conf/wms.yml`

```yaml
http:
  routers:
    wms:
      rule: "Host(`wms.task-code.com`)"
      entrypoints:
        - websecure
      service: wms-svc
      tls:
        certresolver: le        # auto SSL from Let's Encrypt

  services:
    wms-svc:
      loadBalancer:
        servers:
          - url: "http://172.18.0.1:8001"   # host machine as seen from Docker
```

Traefik picks this up automatically — no restart needed.

### 4. Firewall

```bash
ufw allow from 172.18.0.0/16 to any port 8001
```

### 5. DNS (Cloudflare)

Add an A record: `wms` → `188.245.64.189` (DNS only, not proxied).

### Common commands

```bash
systemctl status wms-backend          # check if running
systemctl restart wms-backend         # restart after code changes
journalctl -u wms-backend -n 50       # view logs
curl http://172.18.0.1:8001/          # test backend reachable from host
```

---

## API Overview

All endpoints require authentication via the `access_token` cookie (set at login).

| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Login — sets cookies |
| POST | `/api/auth/logout` | Clear cookies |
| GET | `/api/auth/me` | Current user + business |
| GET | `/api/products` | List SKUs |
| POST | `/api/products` | Create SKU |
| PATCH | `/api/products/{id}` | Update SKU |
| DELETE | `/api/products/{id}` | Delete SKU |
| GET | `/api/inventory` | Stock levels |
| POST | `/api/inventory/movement` | Record stock movement |
| GET | `/api/inventory/movements` | Movement history |
| GET | `/api/inventory/reorder-suggestions` | AI reorder alerts |
| GET | `/api/orders` | List orders |
| POST | `/api/orders` | Create order |
| GET | `/api/orders/{id}` | Order detail |
| PATCH | `/api/orders/{id}/status` | Update status |
| POST | `/api/orders/{id}/complete` | Complete order (updates stock) |
| GET | `/api/customers/analysis` | RFM customer analysis |
| GET | `/api/datasets` | List uploaded datasets |
| POST | `/api/datasets` | Upload CSV |
| POST | `/api/predictions/run` | Run sales forecast |
| GET | `/api/predictions` | List past predictions |

---

## ML Model

The sales forecast uses a pre-trained Random Forest model (`models/sales_model.pkl`). The artifact contains:

- `model` — the fitted estimator
- `date_col`, `target_col` — column names expected in the uploaded CSV
- `extra_features` — optional override features (`temperature`, `promo`, `marketing_spend`)
- `feature_names` — ordered list of features the model expects

Features engineered at inference time: day-of-week, month, quarter, is_weekend, is_month_end, lag_1/3/7/14/30, rolling_mean_7/30, rolling_std_7.
