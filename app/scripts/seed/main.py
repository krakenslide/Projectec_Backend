from app.core.database import SessionLocal
from app.scripts.seed.seed import seed_database


def main():
    db = SessionLocal()

    try:
        seed_database(
            db=db,
            user_count=100,
            organization_count=10,
            ticket_count=None,  # Random tickets per project
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
