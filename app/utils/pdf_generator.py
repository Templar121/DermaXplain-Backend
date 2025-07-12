import os
import base64
import re
import uuid
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors

def generate_pdf_report(user: dict, scan: dict, pdf_path: str):
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    margin = 40
    y = height - margin

    # --- Header ---
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.HexColor("#003f5c"))
    c.drawCentredString(width / 2, y, "DermaXplain – Skin Scan Diagnostic Report")
    
    y -= 14
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.grey)
    c.drawCentredString(width / 2, y, "A product of Lumenary Inc. | Generated: " + datetime.now().strftime('%d %b %Y'))

    # Separator
    y -= 10
    c.setStrokeColor(colors.lightgrey)
    c.setLineWidth(0.6)
    c.line(margin, y, width - margin, y)
    y -= 20

    # --- User & Patient Info ---
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.black)
    c.drawString(margin, y, "User Info")
    c.drawString(width / 2 + 10, y, "Patient Info")
    c.setFont("Helvetica", 9)
    y -= 14

    c.drawString(margin, y, f"Name: {user.get('name', 'N/A')}")
    c.drawString(width / 2 + 10, y, f"Name: {scan.get('patient_name', 'N/A')}")
    y -= 12
    c.drawString(margin, y, f"Email: {user.get('email', 'N/A')}")
    c.drawString(width / 2 + 10, y, f"Age: {scan.get('patient_age', 'N/A')}, Gender: {scan.get('gender', 'N/A')}")
    y -= 12
    c.drawString(width / 2 + 10, y, f"Scan Area: {scan.get('scan_area', 'N/A')}")
    y -= 12
    c.drawString(width / 2 + 10, y, f"Notes: {scan.get('additional_info', 'N/A')}")

    # --- Prediction ---
    y -= 22
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor("#2a9d8f"))
    c.drawString(margin, y, "AI Prediction")
    pred = scan.get("prediction", {})
    readable = pred.get("readable_name", pred.get("class", "N/A"))
    conf_pct = pred.get("confidence", 0.0) * 100

    c.setFont("Helvetica", 9)
    y -= 14
    c.setFillColor(colors.black)
    c.drawString(margin, y, f"Prediction: {readable} ({pred.get('class', '').upper()})")
    y -= 12
    c.drawString(margin, y, f"Confidence Score: {conf_pct:.2f}%")

    # --- Scan Image ---
    y -= 20
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor("#264653"))
    c.drawString(margin, y, "Scan Image")
    y -= 130
    draw_image_from_base64(scan.get("image_base64"), c, x=margin, y=y, w=160, h=120)

    # --- Explanation Table ---
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin + 180, y + 130, "Model Explanations")
    y -= 10

    shap_b64 = scan.get("explanations", {}).get("shap_base64")
    occ_b64 = scan.get("explanations", {}).get("occlusion_base64")

    if shap_b64 or occ_b64:
        y -= 130
        draw_image_from_base64(shap_b64, c, x=margin + 180, y=y + 130, w=130, h=110)
        draw_image_from_base64(occ_b64, c, x=margin + 330, y=y + 130, w=130, h=110)
        c.setFont("Helvetica", 8)
        c.drawCentredString(margin + 245, y + 10, "SHAP Explanation")
        c.drawCentredString(margin + 395, y + 10, "Occlusion Map")

    # --- Disclaimer ---
    y = 70
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(colors.darkgray)
    disclaimer = (
        "Disclaimer: This report is generated using AI and is for informational purposes only. "
        "It is not a medical diagnosis. Please consult a licensed dermatologist."
    )
    text = c.beginText(margin, y)
    for line in split_text(disclaimer, 105):
        text.textLine(line)
    c.drawText(text)

    c.setFont("Helvetica", 7)
    c.setFillColor(colors.lightgrey)
    c.drawCentredString(width / 2, 40, "© Lumenary Inc. | DermaXplain – Empowering Dermatology with AI")

    c.save()


def draw_image_from_base64(b64_str, c: canvas.Canvas, x: int, y: int, w: int, h: int):
    try:
        if not b64_str:
            return
        img_data = re.sub(r"^data:image\/[a-zA-Z]+;base64,", "", b64_str)
        img_data += "=" * (-len(img_data) % 4)

        os.makedirs("temp_uploads", exist_ok=True)
        temp_path = f"temp_uploads/temp_img_{uuid.uuid4().hex}.jpg"
        with open(temp_path, "wb") as f:
            f.write(base64.b64decode(img_data))

        c.drawImage(ImageReader(temp_path), x, y, width=w, height=h, preserveAspectRatio=True)
        os.remove(temp_path)
    except Exception as e:
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.red)
        c.drawString(x, y + 10, f"[Image error: {e}]")
        c.setFillColor(colors.black)


def split_text(text, width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        if len(current + " " + word) <= width:
            current += " " + word if current else word
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines
