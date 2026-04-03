from app.db.session import SessionLocal
from app.openproject.client import OpenProjectClient
from app.services.sync_metadata import MetadataSyncService


def main() -> None:
    db = SessionLocal()
    try:
        result = MetadataSyncService(db, OpenProjectClient()).run()
        print(result)
    finally:
        db.close()


if __name__ == "__main__":
    main()
