from sqlalchemy.orm import declarative_base

# Create the base class for all SQLAlchemy ORM models.
#
# Every model (User, Ticket, Project, etc.) will inherit from this Base.
#
# Base stores metadata about all ORM models:
#   - Table names
#   - Columns
#   - Relationships
#   - Constraints
#
# SQLAlchemy later uses this metadata to:
#   - Generate SQL queries
#   - Create database tables
#   - Perform migrations (Alembic)
#
Base = declarative_base()

"""
What exactly is Base?

Think of it as the parent class of every database model.

For example:

class User(Base):
    ...
class Ticket(Base):
    ...
class Project(Base):
    ...

Every ORM model inherits from the same parent.

What if Base didn't exist?

Suppose you wrote

class User:
    id = Column(...)

Python understands this.

But SQLAlchemy has no idea that this class represents a database table.

To SQLAlchemy it's just:

Normal Python class

It won't create a table.

It won't map rows.

It won't generate SQL.

"""
