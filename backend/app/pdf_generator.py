"""
Generates a cash offer letter PDF using ReportLab.
"""
import io
from datetime import date, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle


def generate_offer_letter(
    property_address: str,
    buyer_name: str,
    buyer_address: str,
    buyer_phone: str,
    buyer_email: str,
    offer_price: float,
    earnest_money: float,
    closing_days: int,
    inspection_days: int,
    strategy: str,
    notes: str = "",
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=1 * inch,
        leftMargin=1 * inch,
        topMargin=1 * inch,
        bottomMargin=1 * inch,
    )
    styles = getSampleStyleSheet()

    heading = ParagraphStyle("heading", parent=styles["Heading1"], fontSize=16, spaceAfter=6)
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=11, leading=16, spaceAfter=8)
    bold_body = ParagraphStyle("bold_body", parent=body, fontName="Helvetica-Bold")
    small = ParagraphStyle("small", parent=styles["Normal"], fontSize=9, leading=12)

    today = date.today()
    closing_date = today + timedelta(days=closing_days)
    inspection_deadline = today + timedelta(days=inspection_days)

    strategy_labels = {
        "wholesale": "Cash / Wholesale",
        "flip": "Cash / Fix & Flip",
        "rental": "Cash / Long-Term Investment",
        "airbnb": "Cash / Short-Term Rental Investment",
    }
    strategy_label = strategy_labels.get(strategy, "Cash")

    story = [
        Paragraph("CASH OFFER TO PURCHASE REAL ESTATE", heading),
        HRFlowable(width="100%", thickness=1, color=colors.black),
        Spacer(1, 0.15 * inch),
        Paragraph(f"Date: {today.strftime('%B %d, %Y')}", body),
        Spacer(1, 0.1 * inch),

        Paragraph("PROPERTY", bold_body),
        Paragraph(property_address, body),
        Spacer(1, 0.1 * inch),

        Paragraph("BUYER", bold_body),
        Paragraph(buyer_name, body),
        Paragraph(buyer_address or "", body),
        Paragraph(f"Phone: {buyer_phone or 'N/A'}  |  Email: {buyer_email or 'N/A'}", small),
        Spacer(1, 0.15 * inch),

        HRFlowable(width="100%", thickness=0.5, color=colors.grey),
        Spacer(1, 0.1 * inch),

        Paragraph("OFFER TERMS", bold_body),
    ]

    terms_data = [
        ["Purchase Price:", f"${offer_price:,.0f}"],
        ["Earnest Money Deposit:", f"${earnest_money:,.0f}"],
        ["Financing:", "CASH — No Financing Contingency"],
        ["Offer Type:", strategy_label],
        ["Proposed Closing Date:", closing_date.strftime("%B %d, %Y") + f" ({closing_days} days from acceptance)"],
        ["Inspection Period:", f"{inspection_days} days from acceptance (deadline: {inspection_deadline.strftime('%B %d, %Y')})"],
    ]
    terms_table = Table(terms_data, colWidths=[2.5 * inch, 4 * inch])
    terms_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("LEADING", (0, 0), (-1, -1), 16),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(terms_table)
    story.append(Spacer(1, 0.2 * inch))

    story += [
        Paragraph("CONDITIONS", bold_body),
        Paragraph(
            "This is a cash offer with no financing contingency. Buyer has the funds available and "
            "can provide proof of funds upon request. This offer is contingent upon satisfactory "
            f"inspection within {inspection_days} days of acceptance.",
            body,
        ),
    ]

    if notes:
        story += [
            Spacer(1, 0.1 * inch),
            Paragraph("ADDITIONAL NOTES", bold_body),
            Paragraph(notes, body),
        ]

    story += [
        Spacer(1, 0.3 * inch),
        HRFlowable(width="100%", thickness=0.5, color=colors.grey),
        Spacer(1, 0.1 * inch),
        Paragraph(
            "This letter is a good-faith expression of interest and is not a legally binding contract. "
            "A formal Purchase and Sale Agreement will be prepared upon acceptance of these terms.",
            small,
        ),
        Spacer(1, 0.4 * inch),
        Paragraph("Buyer Signature: _______________________________   Date: ________________", body),
        Spacer(1, 0.1 * inch),
        Paragraph(f"Printed Name: {buyer_name}", body),
    ]

    doc.build(story)
    return buffer.getvalue()
