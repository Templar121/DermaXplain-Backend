import os
import base64
import re
import uuid
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors

def generate_pdf_report(user: dict, scan: dict, pdf_path: str):
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    y = height - 50  # Top margin

    # Header
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(colors.HexColor("#2B7A78"))
    c.drawString(50, y, "🧴 DermaXplain - Skin Scan Report")
    c.setFillColor(colors.black)

    y -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "User Details")

    c.setFont("Helvetica", 12)
    y -= 20
    c.drawString(60, y, f"Name: {user.get('name', 'N/A')}")
    y -= 18
    c.drawString(60, y, f"Email: {user.get('email', 'N/A')}")

    y -= 30
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Patient & Scan Information")

    c.setFont("Helvetica", 12)
    y -= 20
    c.drawString(60, y, f"Patient Name: {scan.get('patient_name', 'N/A')}")
    y -= 18
    c.drawString(60, y, f"Age: {scan.get('patient_age', 'N/A')}")
    y -= 18
    c.drawString(60, y, f"Gender: {scan.get('gender', 'N/A')}")
    y -= 18
    c.drawString(60, y, f"Scan Area: {scan.get('scan_area', 'N/A')}")
    y -= 18
    c.drawString(60, y, f"Additional Info: {scan.get('additional_info', 'N/A')}")

    y -= 25
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.darkblue)
    c.drawString(60, y, f"Prediction: {scan['prediction']['readable_name']} ({scan['prediction']['class'].upper()})")
    y -= 18
    c.drawString(60, y, f"Confidence Score: {scan['prediction']['confidence'] * 100:.2f}%")
    c.setFillColor(colors.black)

    # Image Section
    y -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Scan Image")

    try:
        image_base64 = scan.get("image_base64")
        if not image_base64:
            raise ValueError("No image data found.")

        # Remove base64 prefix if present
        image_base64 = re.sub(r"^data:image\/[a-zA-Z]+;base64,", "", image_base64)

        # Fix padding if necessary
        padding = len(image_base64) % 4
        if padding:
            image_base64 += "=" * (4 - padding)

        # Decode and save temporarily
        temp_image_path = f"temp_uploads/temp_image_{uuid.uuid4().hex}.jpg"
        with open(temp_image_path, "wb") as f:
            f.write(base64.b64decode(image_base64))

        # Draw image
        c.drawImage(ImageReader(temp_image_path), 50, y - 270, width=300, height=250, preserveAspectRatio=True)

        # Cleanup image
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
    except Exception as e:
        c.setFont("Helvetica-Oblique", 10)
        c.setFillColor(colors.red)
        c.drawString(60, y - 20, f"[Error displaying image: {e}]")
        c.setFillColor(colors.black)

    # Footer / Disclaimer
    c.setFont("Helvetica-Oblique", 9)
    disclaimer_text = (
        "Disclaimer: This report is automatically generated using AI-based predictions and is "
        "intended for informational purposes only. It is not a substitute for professional medical advice. "
        "Always consult a qualified dermatologist for diagnosis and treatment."
    )
    c.drawString(50, 60, disclaimer_text[:120])
    c.drawString(50, 48, disclaimer_text[120:])

    c.setFont("Helvetica", 8)
    c.setFillColor(colors.gray)
    c.drawString(50, 30, "© DermaXplain — Revolutionizing Skin Health with AI")

    c.save()
