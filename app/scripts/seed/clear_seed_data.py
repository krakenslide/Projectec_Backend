from sqlalchemy import delete

from app.core.database import SessionLocal

from app.models.activity import Activity
from app.models.comment import Comment
from app.models.milestone import Milestone
from app.models.ticket import Ticket
from app.models.user_project import UserProject
from app.models.project import Project
from app.models.user_organization import UserOrganization
from app.models.organization import Organization
from app.models.user import User


def clear_database():
    db = SessionLocal()
    try:
        db.execute(delete(Activity))
        db.execute(delete(Comment))
        # Tickets
        db.execute(delete(Ticket))
        # Project child tables
        db.execute(delete(UserProject))
        db.execute(delete(Milestone))
        # Projects
        db.execute(delete(Project))
        # Organization child tables
        db.execute(delete(UserOrganization))
        # Organizations
        db.execute(delete(Organization))
        # Users
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