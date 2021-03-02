import logging

from django.db.models import Q
from django.conf import settings
from django.utils import timezone
from huey import crontab
from huey.contrib.djhuey import db_periodic_task, db_task
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from python_http_client.exceptions import BadRequestsError
from requests.packages.urllib3.util import Retry
from twilio.http.http_client import TwilioHttpClient
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

from notifications.models import Notification, NotificationType


SENDGRID_CLIENT = SendGridAPIClient(settings.SENDGRID_API_KEY)
retry = Retry(
    total=4,
    connect=3,
    read=3,
    status=3,
    backoff_factor=1,
    allowed_methods=["POST"],
    status_forcelist=[500, 501, 502, 503, 504],
)
http_client = TwilioHttpClient(max_retries=retry, timeout=3)
TWILIO_CLIENT = Client(
    settings.TWILIO_ACCOUNT_SID,
    settings.TWILIO_AUTH_TOKEN,
    http_client=http_client,
)


@db_task(name="send_email")
def send_email(notification_id, to_email):
    notification = Notification.objects.get(id=notification_id)

    message = Mail(
        from_email=settings.SENDGRID_FROM_EMAIL,
        to_emails=to_email,
        subject=notification.title,
        html_content=f"<p>{notification.text}</p>",
    )

    try:
        SENDGRID_CLIENT.send(message)
    except BadRequestsError as error:
        logging.error(
            "Fail to send email",
            extra={
                "reason": error.reason,
                "error": error.body.decode(),
            },
        )
    else:
        notification.sent_at = timezone.now()
        notification.save()


@db_task(name="send_sms")
def send_sms(notification_id, phone):
    notification = Notification.objects.get(id=notification_id)
    message = f"{notification.title}\r\n{notification.text}"

    try:
        message = TWILIO_CLIENT.messages.create(
            from_=settings.TWILIO_PHONE_NUMBER, body=message, to=phone
        )
    except TwilioException as error:
        logging.error(
            "Fail to send sms", extra={"code": error.code, "error": error.msg}
        )
    else:
        notification.sent_at = timezone.now()
        notification.save()


@db_task(name="send_notification")
def send_notification(notification_id):
    notification = Notification.objects.select_related("user__profile").get(
        id=notification_id
    )
    profile = notification.user.profile

    if profile.notification_type == NotificationType.SMS:
        send_sms(notification_id, profile.phone.as_e164)
    elif profile.notification_type == NotificationType.EMAIL:
        send_email(notification_id, profile.email)
    else:
        notification.sent_at = timezone.now()
        notification.save()


@db_periodic_task(crontab(minute="*"))
def send_scheduled_notifications():
    now = timezone.now()
    queryset = Notification.objects.filter(
        Q(Q(send_at__isnull=True) | Q(send_at__lte=now)),
        sent_at__isnull=True,
    )

    for notification_id in queryset.values_list("id", flat=True):
        send_notification(notification_id)
