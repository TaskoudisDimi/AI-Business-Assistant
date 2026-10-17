"""Download every file in the Supabase Storage "datasets" bucket into a folder
(used by backup_db.sh)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from db.supabase_client import supabase  # noqa: E402

BUCKET = "datasets"


def walk(prefix: str = ""):
    offset = 0
    while True:
        items = supabase.storage.from_(BUCKET).list(prefix, {"limit": 1000, "offset": offset})
        for it in items:
            path = f"{prefix}/{it['name']}" if prefix else it["name"]
            if it.get("id") is None:      # folders have no id
                yield from walk(path)
            else:
                yield path
        if len(items) < 1000:
            return
        offset += 1000


def main(dest: str) -> None:
    out = Path(dest)
    out.mkdir(parents=True, exist_ok=True)
    count = 0
    for path in walk():
        target = out / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(supabase.storage.from_(BUCKET).download(path))
        count += 1
    print(f"{count} file(s) saved to {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "storage-backup")
