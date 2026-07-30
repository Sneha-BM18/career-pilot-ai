"""
Generates a professional PDF placement report using ReportLab, including
a QR code (via the `qrcode` library) and an institution-style header.
"""
import io
import qrcode
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

PRIMARY_HEX = colors.HexColor("#2563EB")
SUCCESS_HEX = colors.HexColor("#22C55E")
WARNING_HEX = colors.HexColor("#F59E0B")


def _qr_image(data: str, size_px=120):
    qr = qrcode.QRCode(box_size=4, border=1)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#2563EB", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def build_report(student, prediction, salary, career, skills, resume, companies) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=18 * mm, bottomMargin=16 * mm,
                             leftMargin=18 * mm, rightMargin=18 * mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleCP", parent=styles["Title"], textColor=PRIMARY_HEX, fontSize=20)
    h2 = ParagraphStyle("H2CP", parent=styles["Heading2"], textColor=PRIMARY_HEX, spaceBefore=14, fontSize=13)
    normal = styles["BodyText"]
    small = ParagraphStyle("SmallCP", parent=styles["BodyText"], fontSize=8.5, textColor=colors.grey)

    elements = []

    # Header
    header_data = [[
        Paragraph("<b>CareerPilot AI</b><br/><font size=8 color='grey'>AI-Powered Placement Prediction &amp; Career Guidance</font>", title_style),
        Image(_qr_image(f"CareerPilotAI-Report-{student['name']}-{datetime.now().date()}"), width=20 * mm, height=20 * mm),
    ]]
    header_table = Table(header_data, colWidths=[140 * mm, 24 * mm])
    header_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    elements.append(header_table)
    elements.append(HRFlowable(width="100%", color=PRIMARY_HEX, thickness=1.4, spaceAfter=10))

    elements.append(Paragraph(f"<b>Placement Prediction Report</b>", styles["Heading1"]))
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')}", small))
    elements.append(Spacer(1, 8))

    # Student details table
    elements.append(Paragraph("Student Details", h2))
    details = [
        ["Name", student["name"], "Department", student["department"]],
        ["Age", str(student["age"]), "Gender", student["gender"]],
        ["Degree", student["degree"], "CGPA", str(student["cgpa"])],
        ["Internships", str(student["internships"]), "Projects", str(student["projects"])],
    ]
    t = Table(details, colWidths=[35 * mm, 55 * mm, 35 * mm, 45 * mm])
    t.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.grey),
        ("TEXTCOLOR", (2, 0), (2, -1), colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E2E8F0")),
    ]))
    elements.append(t)

    # Prediction result
    elements.append(Paragraph("Prediction Result", h2))
    status_color = SUCCESS_HEX if prediction["status"] == "Placed" else WARNING_HEX
    pred_table = Table([
        ["Placement Status", "Probability", "Confidence", "Risk Score"],
        [prediction["status"], f"{prediction['probability']}%", prediction["confidence"], f"{prediction['risk_score']}%"],
    ], colWidths=[42.5 * mm] * 4)
    pred_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EFF6FF")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 1), (0, 1), status_color),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E2E8F0")),
    ]))
    elements.append(pred_table)

    # Salary
    elements.append(Paragraph("Salary Prediction", h2))
    sal_table = Table([
        ["Minimum", "Expected", "Maximum"],
        [f"₹{salary['min']} LPA", f"₹{salary['expected']} LPA", f"₹{salary['max']} LPA"],
    ], colWidths=[56.7 * mm] * 3)
    sal_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F0FDF4")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E2E8F0")),
    ]))
    elements.append(sal_table)

    # Career suggestions
    elements.append(Paragraph("Career Suggestions", h2))
    elements.append(Paragraph(career["focus"], normal))
    elements.append(Paragraph("Suggested roles: " + ", ".join(career["paths"]), normal))

    # Recommended companies
    elements.append(Paragraph("Recommended Companies", h2))
    top_companies = [c for c in companies if c["eligible"]][:6]
    if top_companies:
        rows = [["Company", "Tier", "Fit Score"]] + [[c["name"], c["tier"], f"{c['fit_score']}%"] for c in top_companies]
        ct = Table(rows, colWidths=[60 * mm, 60 * mm, 50 * mm])
        ct.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EFF6FF")),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E2E8F0")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(ct)
    else:
        elements.append(Paragraph("Keep building your profile — no strong matches yet at current stats.", normal))

    # Skill gap
    elements.append(Paragraph("Skill Gap Analysis (Top Priorities)", h2))
    top_skills = skills[:5]
    rows = [["Skill", "Current", "Required", "Priority"]] + [[s["skill"], f"{s['current']}%", f"{s['required']}%", s["priority"]] for s in top_skills]
    st_table = Table(rows, colWidths=[45 * mm, 35 * mm, 35 * mm, 55 * mm])
    st_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FFFBEB")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E2E8F0")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(st_table)

    # Resume tips
    elements.append(Paragraph("Resume Tips", h2))
    elements.append(Paragraph(f"ATS Resume Score: <b>{resume['score']}/100</b>", normal))
    for tip in resume["tips"][:5]:
        elements.append(Paragraph(f"• {tip}", normal))

    elements.append(Spacer(1, 14))
    elements.append(HRFlowable(width="100%", color=colors.HexColor("#E2E8F0"), thickness=0.8))
    elements.append(Paragraph("CareerPilot AI — AI-Powered Placement Prediction & Career Guidance Platform", small))
    elements.append(Paragraph("This report is AI-generated for guidance purposes and does not guarantee placement outcomes.", small))

    doc.build(elements)
    buf.seek(0)
    return buf.getvalue()
