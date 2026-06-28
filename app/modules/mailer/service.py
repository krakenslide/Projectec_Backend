import resend
from email_validator import validate_email, EmailNotValidError
import os
from dotenv import load_dotenv

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
resend.api_key = RESEND_API_KEY


async def send_verification_email(email: str, token: str):
    verification_link = (
        f"http://127.0.0.1:8000/v1/auth/verify-email?token={token}"
    )

    try:

        response = resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": email,
            "subject": "Verify your email",
            "html": f"""
                <h1>Verify Email</h1>

                <a href="{verification_link}">
                    Verify Account
                </a>
            """
        })

        print("Email sent successfully")
        return {
            "success": True,
            "data": response
        }

    except Exception as e:

        print("Email sending failed")
        print(str(e))

        return {
            "success": False,
            "error": str(e)
        }


async def is_valid_email(email: str) -> bool:
    try:
        validate_email(email)
        return True

    except EmailNotValidError:
        return False