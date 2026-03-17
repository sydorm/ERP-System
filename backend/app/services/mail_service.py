import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def send_email(email_to: str, subject: str, html_content: str):
    """
    Send a system email using SMTP
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning(f"SMTP settings not configured. Email to {email_to} not sent.")
        logger.info(f"Email content:\nSubject: {subject}\nContent: {html_content}")
        return False

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    message["To"] = email_to

    part = MIMEText(html_content, "html")
    message.attach(part)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAILS_FROM_EMAIL, email_to, message.as_string())
        return True
    except Exception as e:
        logger.error(f"Error sending email to {email_to}: {str(e)}")
        return False

async def send_new_password_email(email_to: str, password: str, first_name: str):
    """
    Send email with a new generated password
    """
    subject = f"{settings.PROJECT_NAME} - Ваш новий пароль"
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
                <h2 style="color: #6366f1;">Вітаємо, {first_name}!</h2>
                <p>Адміністратор скинув ваш пароль для доступу до {settings.PROJECT_NAME}.</p>
                <div style="background-color: #f4f5f9; padding: 15px; border-radius: 5px; text-align: center; margin: 20px 0;">
                    <p style="margin: 0; font-size: 14px; color: #64748b;">Ваш новий пароль:</p>
                    <p style="margin: 10px 0 0; font-size: 24px; font-weight: bold; color: #1e1b4b; letter-spacing: 2px;">{password}</p>
                </div>
                <p>Будь ласка, змініть цей пароль після першого входу в налаштуваннях профілю.</p>
                <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 12px; color: #999;">Це автоматичне повідомлення. Будь ласка, не відповідайте на нього.</p>
            </div>
        </body>
    </html>
    """
    return await send_email(email_to, subject, html_content)
