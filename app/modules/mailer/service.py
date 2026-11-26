import resend
from email_validator import validate_email, EmailNotValidError
import os
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
resend.api_key = RESEND_API_KEY


BASE_DIR = Path(__file__).resolve()

template_env = Environment(
    loader=FileSystemLoader(BASE_DIR / "templates")
)



async def send_verification_email(email: str, token: str):
    verification_link = (
    f"https://workorbit.space/verify-email?token={token}"
    )
    template = template_env.get_template("verify_email.html")

    html = template.render(
        verification_link=verification_link
    )

    try:
        response = resend.Emails.send(
            {
                "from": "WorkOrbit <noreply@workorbit.space>",
                "to": [email],
                "subject": "Verify your WorkOrbit email",
                "html": html,
            }
        )

        return {"success": True, "data": response}
    except Exception as e:
        print("Email sending failed")
        print(str(e))

        return {"success": False, "error": str(e)}



# async def send_verification_email(email: str, token: str):
#     verification_link = (
#         f"https://workorbit.space/verify-email?token={token}"
#     )

#     try:
#         response = resend.Emails.send(
#             {
#                 "from": "WorkOrbit <noreply@workorbit.space>",
#                 "to": [email],
#                 "subject": "Verify your WorkOrbit email",
#                 "html": f"""
#                     <h1>Verify your email</h1>

#                     <p>Thanks for signing up for WorkOrbit.</p>

#                     <p>
#                         <a href="{verification_link}">
#                             Verify Account
#                         </a>
#                     </p>

#                     <p>
#                         If you didn't create this account, you can ignore
#                         this email.
#                     </p>
#                 """,
#             }
#         )

#         print("Email sent successfully")
#         return {"success": True, "data": response}

#     except Exception as e:
#         print("Email sending failed")
#         print(str(e))

#         return {"success": False, "error": str(e)}

    
