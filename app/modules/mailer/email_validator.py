import re

EMAIL_REGEX = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)

class EmailValidator:
    @staticmethod
    def validate(email: str):
        if not email:
            raise ValueError("Email cannot be empty")
        if len(email) > 254:
            raise ValueError("Email too long")
        if not EMAIL_REGEX.match(email):
            raise ValueError(f"Invalid email : {email}")