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
        
        
        
def send_deletion_email(to_email: str, name: str):
    subject = "Account Deleted Successfully"
    body = f"""
    Hi {name},

    This is to confirm that your account at SkinSights AI has been successfully deleted.

    We're sorry to see you go. Your data has been permanently removed from our platform.  
    If you ever wish to return, you're always welcome to register again and explore our explainable AI-powered skin diagnostics.

    Thank you for having been a part of SkinSights AI.  
    We wish you all the best.

    Stay healthy and take care,  
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
            print("✅ Deletion confirmation email sent.")
    except Exception as e:
        print(f"❌ Failed to send deletion email: {e}")
