from app.celery_app import celery_app

from repository import EmailRepository
from provider import SMTPProvider


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def send_email_task(self, email_id):
    request = EmailRepository.get(email_id)
    provider = SMTPProvider()
    provider.send(request)
    request.status = "SENT"
    EmailRepository.update(request)