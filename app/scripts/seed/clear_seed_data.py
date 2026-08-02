from sqlalchemy import delete

from app.core.database import SessionLocal

from app.models.comment import Comment
from app.models.ticket import Ticket
from app.models.user_project import UserProject
from app.models.project import Project
from app.models.user_organization import UserOrganization
from app.models.organization import Organization
from app.models.user import User


def clear_database():
    db = SessionLocal()

    try:
        db.execute(delete(Comment))
        db.execute(delete(Ticket))
        db.execute(delete(UserProject))
        db.execute(delete(Project))
        db.execute(delete(UserOrganization))
        db.execute(delete(Organization))
        db.execute(delete(User))

        db.commit()
        print("Database cleared successfully.")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    clear_database()