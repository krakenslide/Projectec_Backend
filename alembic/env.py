import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool, text
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import DATABASE_URL, DB_SCHEMA
from app.models.base import Base

# Import the models package.
# Importing app.models executes models/__init__.py, which in turn imports
# every ORM model (User, Ticket, Project, etc.).
# Every model inherits from Base, and during class creation SQLAlchemy
# automatically registers the model inside Base.metadata.
# Alembic uses Base.metadata to compare the ORM models with the current
# PostgreSQL schema during --autogenerate.
import app.models

# ------------------------------------------------------------------
# Alembic Configuration
# ------------------------------------------------------------------

config = context.config

# Override sqlalchemy.url from alembic.ini using our application config.
config.set_main_option("sqlalchemy.url", DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata containing every registered ORM model.
target_metadata = Base.metadata


# ------------------------------------------------------------------
# Tell Alembic which database objects should be included.
# ------------------------------------------------------------------

def include_object(object, name, type_, reflected, compare_to):
    """
    Only migrate objects that belong to our application schema.

    Ignore everything inside PostgreSQL's public schema.
    """
    if type_ == "table":
        return object.schema == DB_SCHEMA

    return True


# ------------------------------------------------------------------
# Offline Migrations
# ------------------------------------------------------------------

def run_migrations_offline():
    """
    Generate SQL without connecting to the database.

    Used mainly for:
        alembic upgrade --sql
    """

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,

        # SQLAlchemy metadata containing all ORM models.
        target_metadata=target_metadata,

        # Render literal values inside generated SQL.
        literal_binds=True,

        dialect_opts={
            "paramstyle": "named",
        },

        # Store alembic_version inside our schema.
        version_table_schema=DB_SCHEMA,

        # Compare all schemas instead of only public.
        include_schemas=True,

        # Ignore objects outside our schema.
        include_object=include_object,

        # Detect datatype changes.
        compare_type=True,

        # Detect server_default changes.
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ------------------------------------------------------------------
# Online Migrations
# ------------------------------------------------------------------

def do_run_migrations(connection):
    """
    Configure Alembic using an active database connection.
    """

    context.configure(
        connection=connection,

        # SQLAlchemy metadata.
        target_metadata=target_metadata,

        # Store alembic_version in our schema.
        version_table_schema=DB_SCHEMA,

        # Compare across schemas.
        include_schemas=True,

        # Ignore tables outside our schema.
        include_object=include_object,

        # Detect datatype modifications.
        compare_type=True,

        # Detect default value changes.
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """
    Connect to PostgreSQL and execute migrations.
    """

    engine = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with engine.begin() as connection:

        # Create the schema automatically if it doesn't exist.
        await connection.execute(
            text(f'CREATE SCHEMA IF NOT EXISTS "{DB_SCHEMA}"')
        )

        await connection.run_sync(do_run_migrations)

    await engine.dispose()


# ------------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())

#import app.models magic explained
"""
Now Alembic executes
import app.models

Notice:
It is NOT
import app.models.user

It is importing the package.

What Python Does

Python sees

app.models

and says

"models is a package."

How does it know?

Because of

models/
    __init__.py

Then Python executes

models/__init__.py

from top to bottom.
so we have all the imports implicitly
"""
###why env.py file was required
"""
Read the Readme contents before reading below notes

You can think of `env.py` as the **bridge** between **Alembic** and **your SQLAlchemy application**.

Without `env.py`, Alembic has no idea:

* Which database to connect to
* Which models to compare
* Which metadata to inspect
* Whether to use sync or async connections
* Which schema to migrate

---

## Here's what happens when you run:

```bash
alembic revision --autogenerate -m "Initial schema"
```

Internally:

```text
                 Alembic CLI
                      │
                      ▼
                Executes env.py
                      │
         ┌────────────┼────────────┐
         ▼            ▼            ▼
   DATABASE_URL   Base.metadata   Engine
         │            │            │
         └────────────┼────────────┘
                      ▼
          Compare Models vs Database
                      ▼
          Generate Migration File
```

Notice that **Alembic itself never imports your models directly**.

It simply executes `env.py`.

---

## What does `env.py` provide?

### 1. Database connection

```python
config.set_main_option(
    "sqlalchemy.url",
    DATABASE_URL,
)
```

Alembic now knows:

> "Connect to this PostgreSQL database."

---

### 2. Import models

```python
import app.models
```

This executes:

```python
class User(Base):
```

```python
class Ticket(Base):
```

```python
class Project(Base):
```

Every model registers itself in:

```python
Base.metadata
```

---

### 3. Tell Alembic which metadata to inspect

```python
target_metadata = Base.metadata
```

This is probably the single most important line.

Now Alembic knows:

> "These are the models I'm responsible for."

---

### 4. Configure comparison

```python
context.configure(
    connection=connection,
    target_metadata=target_metadata,
)
```

This tells Alembic:

> Compare **this metadata** with **this database**.

---

### 5. Run comparison

Finally:

```python
context.run_migrations()
```

This triggers the comparison and migration generation.

---

# Imagine `env.py` didn't exist

Suppose you run:

```bash
alembic revision --autogenerate
```

Alembic asks:

```text
Where is PostgreSQL?

Where are your models?

What metadata should I inspect?

Should I use sync or async engine?
```

Nobody answers.

Autogeneration cannot happen.

---

# My favorite analogy

Think of a restaurant.

### Alembic

The chef.

### SQLAlchemy Models

The recipe.

### PostgreSQL

The kitchen.

### env.py

The waiter who brings the recipe to the chef.

Without the waiter:

```text
Chef: "What should I cook?"

...
```

No recipe arrives.

No food gets cooked.

---

# One last thing

When you first open `env.py`, it feels like a lot of boilerplate.

That's because **95% of it rarely changes**.

In most projects, after you configure it once, you almost never touch it again. Day-to-day, your workflow becomes:

1. Modify your SQLAlchemy models.
2. Run:

   ```bash
   alembic revision --autogenerate -m "..."
   ```
3. Review the generated migration.
4. Run:

   ```bash
   alembic upgrade head
   ```

`env.py` quietly does its job in the background every time, acting as the adapter between Alembic and your application's ORM configuration.

"""
