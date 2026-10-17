"""
Daily alert emails: reorder needs, lots expiring soon, unusual activity.
Sent to owners/admins of every business with alerts enabled, at most once a day,
and only when there's something to report. Run from cron / a systemd timer:

    cd wms/backend && venv/bin/python scripts/send_alerts.py
"""
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from db.supabase_client import supabase  # noqa: E402
from services import mailer  # noqa: E402
from services.alerts import build_digest, recipients, send_digest  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("alerts")


def main() -> int:
    if not mailer.is_configured():
        log.warning("SMTP not configured — nothing sent")
        return 0
    today = datetime.now(timezone.utc).date()
    businesses = supabase.table("businesses").select("id, name, alert_last_sent_at") \
        .eq("alert_email_enabled", True).execute().data or []
    sent = 0
    for b in businesses:
        last = b.get("alert_last_sent_at")
        if last and datetime.fromisoformat(last.replace("Z", "+00:00")).date() >= today:
            continue
        try:
            digest = build_digest(b["id"])
            if digest["count"] == 0:
                continue
            to = recipients(b["id"])
            if not to:
                continue
            send_digest(b["id"], b["name"], to, digest)
            supabase.table("businesses").update({"alert_last_sent_at": datetime.now(timezone.utc).isoformat()}) \
                .eq("id", b["id"]).execute()
            sent += 1
            log.info("sent %s items to %s recipient(s) for %s", digest["count"], len(to), b["name"])
        except Exception:
            log.exception("failed for business %s", b["id"])
    log.info("done: %s business(es) emailed", sent)
    return 0


if __name__ == "__main__":
    sys.exit(main())
