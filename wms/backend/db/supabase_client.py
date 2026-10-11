from supabase import create_client, Client
from supabase.lib.client_options import SyncClientOptions
from core.config import SUPABASE_URL, SUPABASE_KEY

# Service-role client for database/storage access. Never call sign_in / sign_out /
# refresh_session on it: supabase-py swaps the client's Authorization header to the
# signed-in user's JWT, which would leak into every other request.
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def new_auth_client() -> Client:
    """Fresh, stateless client for per-request auth flows (login, refresh, reset)."""
    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
        options=SyncClientOptions(
            auto_refresh_token=False,
            persist_session=False,
            flow_type="implicit",
        ),
    )
