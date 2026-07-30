from sqlalchemy.orm import Session

from app.models.user import User
from app.scripts.seed.config import DEFAULT_PASSWORD_HASH
from app.scripts.seed.context import SeedContext


def seed_users(
    db: Session,
    context: SeedContext,
    user_count: int,
) -> None:
    users: list[User] = []

    for _ in range(user_count):
        user = User(
            name=context.faker.name(),
            email=context.faker.unique.email(),
            password_hash=DEFAULT_PASSWORD_HASH,
            phone_number = context.faker.numerify("##########"),
            nationality="India",
            verification_token=None,
            is_verified=True,
            is_active=True,
            two_factor_enabled=False,
            is_deleted=False,
        )

        users.append(user)

    db.add_all(users)
    db.flush()

    context.users.extend(users)

    for user in users:
        context.user_map[user.id] = user