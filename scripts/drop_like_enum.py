import sys
from pathlib import Path
from sqlalchemy import create_engine, text

# ensure project root is on sys.path so `app` imports work
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.core.settings.settings import settings


if __name__ == "__main__":
    e = create_engine(settings.db_url_sync)
    try:
        with e.begin() as c:
            c.execute(text("DROP TYPE IF EXISTS linap.like_target CASCADE"))
        print("OK: dropped type linap.like_target (if existed)")
    except Exception as exc:
        print("ERROR:", exc)
        raise
