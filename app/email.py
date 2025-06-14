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
    subject = "🎉 Registration Successful - Welcome to SkinSights AI!"

    body_html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f4f6f7;
                padding: 30px;
                color: #333;
            }}
            .container {{
                background-color: #ffffff;
                padding: 30px;
                max-width: 600px;
                margin: auto;
                border-radius: 10px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
            }}
            h1 {{
                color: #2E86C1;
                font-size: 22px;
            }}
            p {{
                line-height: 1.6;
                font-size: 15px;
            }}
            .footer {{
                margin-top: 30px;
                font-size: 12px;
                color: #777;
                border-top: 1px solid #ddd;
                padding-top: 15px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome, {name} 👋</h1>
            <p>We're thrilled to have you on board at <strong>SkinSights AI</strong>!</p>
            <p>
                You have successfully registered at SkinSights AI, your trusted platform for explainable skin cancer detection and insights.
            </p>
            <p>
                With our cutting-edge AI, you can confidently analyze skin images for potential concerns, supported by transparent and interpretable results.
            </p>
            <p>
                Thank you for joining our mission to make advanced skin diagnostics accessible, reliable, and understandable.
            </p>
            <p>If you have any questions or need assistance, feel free to reach out to our support team anytime.</p>
            <p>Stay safe and healthy,<br><em>The SkinSights AI Team</em></p>
            <div class="footer">
                This is an automated message. Please do not reply to this email.  
                For help, visit our support page or contact us directly through the app.
            </div>
        </div>
    </body>
    </html>
    """

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg.set_content("Welcome to SkinSights AI! Please view this email in an HTML-compatible client.")
    msg.add_alternative(body_html, subtype="html")

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
    
    # Styled HTML content
    body_html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                color: #333;
                background-color: #f9f9f9;
                padding: 20px;
            }}
            .container {{
                background-color: #ffffff;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0,0,0,0.05);
                max-width: 600px;
                margin: auto;
            }}
            .header {{
                font-size: 20px;
                font-weight: bold;
                color: #2E86C1;
                margin-bottom: 20px;
            }}
            .footer {{
                margin-top: 30px;
                font-size: 13px;
                color: #888;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">Account Deletion Confirmation</div>
            <p>Hi {name},</p>
            <p>
                This is to confirm that your account at <strong>SkinSights AI</strong> has been successfully deleted.
            </p>
            <p>
                We're sorry to see you go. Your data has been permanently removed from our platform.
                If you ever wish to return, you're always welcome to register again and explore our explainable AI-powered skin diagnostics.
            </p>
            <p>
                Thank you for having been a part of <strong>SkinSights AI</strong>.  
                We wish you all the best.
            </p>
            <p>Stay healthy and take care,</p>
            <p><em>The SkinSights AI Team</em></p>
            <div class="footer">
                This is an automated message. Please do not reply to this email.
            </div>
        </div>
    </body>
    </html>
    """

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg.set_content("This is a HTML email. Please view it in an HTML-compatible email client.")
    msg.add_alternative(body_html, subtype="html")

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print("✅ Deletion confirmation email sent.")
    except Exception as e:
        print(f"❌ Failed to send deletion email: {e}")
