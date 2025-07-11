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
    subject = "🎉 Welcome to DermaXplain! Your Registration is Confirmed"

    # HTML body with hero banner, button, and social links
    body_html = f"""
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #74ABE2 0%, #5563DE 100%);
                color: #333;
            }}
            .container {{
                background-color: #ffffff;
                max-width: 600px;
                margin: 40px auto;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 8px 20px rgba(0,0,0,0.1);
            }}
            .hero {{
                width: 100%;
                height: 200px;
                background: url('https://example.com/skin-sights-hero.jpg') center/cover no-repeat;
            }}
            .content {{
                padding: 30px;
            }}
            h1 {{
                color: #5563DE;
                font-size: 24px;
                margin-bottom: 10px;
            }}
            p {{
                line-height: 1.6;
                font-size: 16px;
                margin: 16px 0;
            }}
            .button {{
                display: inline-block;
                background-color: #74ABE2;
                color: #ffffff !important;
                text-decoration: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                margin: 20px 0;
            }}
            .divider {{
                border: none;
                height: 1px;
                background: #eee;
                margin: 20px 0;
            }}
            .footer {{
                font-size: 12px;
                color: #777;
                padding: 20px 30px;
                text-align: center;
            }}
            .social-icons img {{
                width: 24px;
                margin: 0 6px;
                vertical-align: middle;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="hero"></div>
            <div class="content">
                <h1>Welcome, {name}! 👋</h1>
                <p>We’re excited to have you join the <strong>DermaXplain</strong> community!</p>
                <p>DermaXplain leverages state-of-the-art machine learning to deliver transparent, interpretable skin diagnostics—empowering you with insights you can trust.</p>
                <a href="https://skinsights.ai/dashboard" class="button">Go to Your Dashboard</a>
                <p>To get started:</p>
                <ul>
                    <li>Upload your first skin image for analysis</li>
                    <li>Explore detailed reports with interactive charts</li>
                    <li>Stay updated with our latest features and tips</li>
                </ul>
                <p>If you have any questions, our support team is here to help at <a href="mailto:support@skinsights.ai">support@skinsights.ai</a>.</p>
                <hr class="divider" />
                <p><strong>Follow us on:</strong></p>
                <p class="social-icons">
                    <a href="https://twitter.com/skinsights"><img src="https://example.com/icons/twitter.png" alt="Twitter" /></a>
                    <a href="https://linkedin.com/company/skinsights"><img src="https://example.com/icons/linkedin.png" alt="LinkedIn" /></a>
                    <a href="https://instagram.com/skinsights.ai"><img src="https://example.com/icons/instagram.png" alt="Instagram" /></a>
                </p>
            </div>
            <div class="footer">
                This is an automated email—please do not reply to this message.<br />
                &copy; {2025} DermaXplain. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """

    _send_email(to_email, subject, body_html)
        
        
        
def send_deletion_email(to_email: str, name: str):
    subject = "😔 Your DermaXplain Account Has Been Deleted"

    # HTML body with clean design, button to rejoin, and support link
    body_html = f"""
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #fafafa;
                color: #333;
            }}
            .container {{
                background-color: #ffffff;
                max-width: 600px;
                margin: 40px auto;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 6px 18px rgba(0,0,0,0.08);
            }}
            .content {{
                padding: 30px;
            }}
            h1 {{
                color: #E74C3C;
                font-size: 22px;
                margin-bottom: 10px;
            }}
            p {{
                line-height: 1.6;
                font-size: 16px;
                margin: 16px 0;
            }}
            .button {{
                display: inline-block;
                background-color: #E74C3C;
                color: #ffffff !important;
                text-decoration: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                margin: 20px 0;
            }}
            .footer {{
                font-size: 12px;
                color: #777;
                padding: 20px 30px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="content">
                <h1>Hi {name},</h1>
                <p>Your account at <strong>DermaXplain</strong> has been successfully deleted.</p>
                <p>We’re sorry to see you go! All your data has been permanently removed from our platform in accordance with our privacy policy.</p>
                <a href="https://skinsights.ai/register" class="button">Re-register Now</a>
                <p>If you have any feedback or questions, please let us know at <a href="mailto:support@skinsights.ai">support@skinsights.ai</a>. We’d love to hear from you.</p>
                <p>Thank you for being part of our journey. We wish you health and happiness.</p>
                <p><em>The DermaXplain Team</em></p>
            </div>
            <div class="footer">
                This is an automated email—please do not reply.<br />
                &copy; {2025} DermaXplain. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """
    _send_email(to_email, subject, body_html)
    
    
def send_admin_deletion_email(to_email: str, name: str):
    subject = "⚠️ Your DermaXplain Account Was Deleted by Admin"

    body_html = f"""
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #fafafa;
                color: #333;
            }}
            .container {{
                background-color: #ffffff;
                max-width: 600px;
                margin: 40px auto;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 6px 18px rgba(0,0,0,0.08);
            }}
            .content {{
                padding: 30px;
            }}
            h1 {{
                color: #E67E22;
                font-size: 22px;
                margin-bottom: 10px;
            }}
            p {{
                line-height: 1.6;
                font-size: 16px;
                margin: 16px 0;
            }}
            .button {{
                display: inline-block;
                background-color: #E67E22;
                color: #ffffff !important;
                text-decoration: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                margin: 20px 0;
            }}
            .footer {{
                font-size: 12px;
                color: #777;
                padding: 20px 30px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="content">
                <h1>Hello {name},</h1>
                <p>This is to inform you that your account at <strong>DermaXplain</strong> has been deleted by an administrator.</p>
                <p>All of your associated data has been removed as per our platform policy.</p>
                <p>If you believe this action was taken in error or have any concerns, you can reach us at <a href="mailto:support@skinsights.ai">support@skinsights.ai</a>.</p>
                <a href="https://skinsights.ai/register" class="button">Contact Support</a>
                <p>We appreciate your understanding and cooperation.</p>
                <p><em>— The DermaXplain Team</em></p>
            </div>
            <div class="footer">
                This is an automated message—please do not reply directly.<br />
                &copy; {2025} DermaXplain. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """

    _send_email(to_email, subject, body_html)

    
    
def _send_email(to_email: str, subject: str, body_html: str):
    """Helper to construct and send HTML emails"""
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg.set_content("Please view this email in an HTML-compatible client.")
    msg.add_alternative(body_html, subtype='html')

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print(f"✅ Email '{subject}' sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send email '{subject}': {e}")

async def send_reset_email(to_email: str, link: str):
    subject = "🔒 Reset Your DermaXplain Password"

    # HTML body with clean design, button to reset password, and support link
    body_html = f"""
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #fafafa;
                color: #333;
            }}
            .container {{
                background-color: #ffffff;
                max-width: 600px;
                margin: 40px auto;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 6px 18px rgba(0,0,0,0.08);
            }}
            .content {{
                padding: 30px;
            }}
            h1 {{
                color: #3498DB;
                font-size: 22px;
                margin-bottom: 10px;
            }}
            p {{
                line-height: 1.6;
                font-size: 16px;
                margin: 16px 0;
            }}
            .button {{
                display: inline-block;
                background-color: #3498DB;
                color: #ffffff !important;
                text-decoration: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                margin: 20px 0;
            }}
            .footer {{
                font-size: 12px;
                color: #777;
                padding: 20px 30px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="content">
                <h1>Password Reset Requested</h1>
                <p>Hello,</p>
                <p>We received a request to reset the password for your <strong>DermaXplain</strong> account (<em>{to_email}</em>).</p>
                <p>Click the button below to choose a new password. This link will expire in 60 minutes for your security.</p>
                <a href="{link}" class="button">Reset My Password</a>
                <p>If you didn’t request a password reset, you can safely ignore this email. No changes were made to your account.</p>
                <p>If you have any questions or need further assistance, please contact our support team at <a href="mailto:support@skinsights.ai">support@skinsights.ai</a>.</p>
                <p>Stay safe,<br /><em>The DermaXplain Team</em></p>
            </div>
            <div class="footer">
                This is an automated email—please do not reply.<br />
                &copy; {2025} DermaXplain. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """
    _send_email(to_email, subject, body_html)
