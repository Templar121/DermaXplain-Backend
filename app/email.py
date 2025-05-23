import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_registration_email(to_email: str, name: str):
    subject = "Registration Successful"
    body = f"""
    Hi {name},

    🎉 Welcome to SkinSights AI!

    We're excited to have you on board. You have successfully registered at SkinSights AI, your trusted platform for explainable skin cancer detection and insights.

    With SkinSights AI, you can confidently analyze skin images with state-of-the-art AI technology that not only detects potential concerns but also provides clear, understandable explanations to help you make informed decisions.

    Thank you for joining our mission to bring advanced, transparent AI diagnostics to everyone.

    If you have any questions or need assistance, feel free to reach out to our support team.

    Stay safe and healthy,  
    The SkinSights AI Team
"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print("✅ Registration email sent.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
