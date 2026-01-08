import smtplib
from email.mime.text import MIMEText
from app.core.config import settings

def send_verification_email(to_email: str, verify_link: str):
    # If SMTP not configured => print link (DEV)
    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASS:
        print("\n=== SAI DEVION VERIFY LINK (DEV) ===")
        print(f"To: {to_email}")
        print(verify_link)
        print("===================================\n")
        return

    msg = MIMEText(f"Verify your email:\n\n{verify_link}\n")
    msg["Subject"] = "SAI Devion - Verify your email"
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg)
