import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

def send_email(to: str, subject: str, html_body: str):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = to
        msg.attach(MIMEText(html_body, "html"))
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.sendmail(settings.SMTP_USER, to, msg.as_string())
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False

def send_password_reset_email(to: str, name: str, reset_link: str):
    html = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:auto;padding:30px;">
      <h2 style="color:#2563eb">CampusConnect</h2>
      <p>Hi <strong>{name}</strong>,</p>
      <p>You requested a password reset. Click the button below to set a new password:</p>
      <a href="{reset_link}" style="display:inline-block;background:#2563eb;color:#fff;
         padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:700;margin:16px 0">
        Reset Password
      </a>
      <p style="color:#64748b;font-size:12px">This link expires in 30 minutes.<br>
      If you didn't request this, ignore this email.</p>
    </div>"""
    send_email(to, "Reset your CampusConnect password", html)

def send_notification_email(to: str, name: str, title: str, body: str):
    html = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:auto;padding:30px;">
      <h2 style="color:#2563eb">CampusConnect</h2>
      <p>Hi <strong>{name}</strong>,</p>
      <h3>{title}</h3>
      <p>{body}</p>
    </div>"""
    send_email(to, f"[CampusConnect] {title}", html)
