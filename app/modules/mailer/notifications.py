from app.celery_app import celery_app
import requests

@celery_app.task(queue="email")
def send_email_notification(
    recipient: str,
    subject: str,
    message: str
):
    print(f"Sending email to {recipient}")
    payload = {
        "recipient": recipient,
        "subject": subject,
        "message": message,
    }

    # SMTP Logic goes here
    response = requests.post(
        "https://webhook.site/81007c8f-66d0-4b08-a7e6-9c16fdc95fdb",
        json=payload,
        timeout=10,
    )

    response.raise_for_status()

    print("Webhook sent successfully")

    print("Email sent")