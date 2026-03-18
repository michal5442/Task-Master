import logging
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from typing import Dict

from todo_service import get_tasks

logger = logging.getLogger(__name__)


def _env_flag(name: str, default: bool = False) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def _send_email(subject: str, body: str) -> bool:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    reminder_to = os.getenv("REMINDER_TO_EMAIL")
    reminder_from = os.getenv("REMINDER_FROM_EMAIL") or smtp_username
    use_tls = _env_flag("SMTP_USE_TLS", default=True)

    if not smtp_host or not reminder_to or not reminder_from:
        logger.debug("SMTP not configured for reminders")
        return False

    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = reminder_from
    msg["To"] = reminder_to

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            if use_tls:
                server.starttls()
            if smtp_username and smtp_password:
                server.login(smtp_username, smtp_password)
            server.sendmail(reminder_from, [reminder_to], msg.as_string())
        return True
    except Exception as exc:
        logger.error("Failed to send reminder email: %s", exc)
        return False


def check_and_send_reminders() -> Dict[str, int]:
    """Scan due tasks and send one-time email reminders."""
    checked = 0
    sent = 0
    tasks = get_tasks()["tasks"]

    for task in tasks:
        if task.get("completed"):
            continue

        due_date = task.get("due_date")
        if not due_date:
            continue

        checked += 1
        if task.get("reminder_sent"):
            continue

        try:
            due_dt = datetime.fromisoformat(due_date)
        except ValueError:
            logger.warning("Invalid due_date format for task %s: %s", task.get("id"), due_date)
            continue

        now = datetime.now(due_dt.tzinfo) if due_dt.tzinfo else datetime.now()
        if now < due_dt:
            continue

        subject = f"תזכורת למשימה #{task.get('id')}: {task.get('title', '')}"
        body = (
            "זוהי תזכורת אוטומטית מהמערכת.\n\n"
            f"מזהה משימה: {task.get('id')}\n"
            f"כותרת: {task.get('title', '')}\n"
            f"תיאור: {task.get('description', '')}\n"
            f"תאריך יעד: {due_date}\n"
        )

        if _send_email(subject, body):
            task["reminder_sent"] = True
            task["reminder_sent_at"] = now.isoformat()
            sent += 1

    return {"checked": checked, "sent": sent}
