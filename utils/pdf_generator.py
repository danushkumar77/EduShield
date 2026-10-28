"""
========================================================================
   EDUSHIELD: PDF ASSESSMENT REPORT GENERATOR
   pdf_generator.py: Creates professional student retention reports.
========================================================================
"""
import os
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_prediction_pdf(record):
    """
    Generates a beautifully styled PDF report in memory for a given prediction record.
    Returns a BytesIO stream containing the PDF binary.
    """
    buffer = BytesIO()
    
    # Page setup - 0.75 in margin
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Define custom cohesive color scheme (Matched to Logo: Cobalt Blue and Violet Purple)
    primary_color = colors.HexColor('#1d4ed8')  # Cobalt Blue
    secondary_color = colors.HexColor('#581c87')  # Violet Purple
    dark_text = colors.HexColor('#1e293b')      # Slate 800
    light_bg = colors.HexColor('#f8fafc')       # Slate 50
    border_color = colors.HexColor('#e2e8f0')   # Slate 200
    
    # Alert banner colors based on risk
    risk_level = record.get('risk_level', 'Low')
    if risk_level == 'High':
        risk_bg = colors.HexColor('#fee2e2')    # Light Red
        risk_text_color = colors.HexColor('#b91c1c') # Red 700
    elif risk_level == 'Medium':
        risk_bg = colors.HexColor('#fef3c7')    # Light Amber
        risk_text_color = colors.HexColor('#b45309') # Amber 700
    else:
        risk_bg = colors.HexColor('#dcfce7')    # Light Green
        risk_text_color = colors.HexColor('#15803d') # Green 700

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=15
    )
    
    h2_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=secondary_color,
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=dark_text
    )
    
    body_bold = ParagraphStyle(
        'BodyTextBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    risk_banner_style = ParagraphStyle(
        'RiskBanner',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=risk_text_color,
        alignment=1 # Center aligned
    )
    
    rec_item_style = ParagraphStyle(
        'RecItem',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    story = []
    
    # 1. Header Banner
    story.append(Paragraph("EDUSHIELD", title_style))
    story.append(Paragraph("AI-Powered Student Retention Analytics — Risk Assessment Report", subtitle_style))
    story.append(Spacer(1, 5))
    
    # 2. Risk Assessment Verdict Box
    prob_pct = int(record.get('probability', 0.0) * 100)
    conf_pct = record.get('confidence', 85.0)
    verdict = record.get('prediction', 'Not At Risk')
    
    verdict_text = f"RISK LEVEL ASSESSMENT: {risk_level.upper()} ({verdict.upper()})<br/>" \
                   f"Calculated Dropout Probability: {prob_pct}% | Model Confidence: {conf_pct}%"
                   
    verdict_p = Paragraph(verdict_text, risk_banner_style)
    
    verdict_table = Table([[verdict_p]], colWidths=[7.0*inch])
    verdict_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), risk_bg),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 15),
        ('RIGHTPADDING', (0,0), (-1,-1), 15),
        ('BOX', (0,0), (-1,-1), 1.5, risk_text_color),
    ]))
    story.append(verdict_table)
    story.append(Spacer(1, 15))
    
    # 3. Student Profile Table
    story.append(Paragraph("Student Intake Demographics", h2_style))
    
    # Course Mapping helper (for display names)
    course_id = int(record['input_data'].get('Course', 9500))
    course_mapping = {
        33: 'Biofuel Production Tech',
        171: 'Animation & Multimedia Design',
        9070: 'Communication Design',
        9085: 'Veterinary Nursing',
        9119: 'Informatics Engineering',
        9130: 'Equiniculture',
        9147: 'Management',
        9238: 'Social Service',
        9254: 'Tourism',
        9500: 'Nursing',
        9556: 'Oral Hygiene',
        9670: 'Advertising & Marketing Management',
        9773: 'Journalism & Communication',
        9853: 'Basic Education',
        9991: 'Management (Evening)'
    }
    course_name = course_mapping.get(course_id, f"Course ID {course_id}")
    
    # Gender
    gender_val = int(record['input_data'].get('Gender', 0))
    gender_text = "Male" if gender_val == 1 else "Female"
    
    # Debtor / Tuition ok
    debtor_val = int(record['input_data'].get('Debtor', 0))
    debtor_text = "Yes" if debtor_val == 1 else "No"
    
    tuition_val = int(record['input_data'].get('Tuition fees up to date', 1))
    tuition_text = "Up to Date" if tuition_val == 1 else "Overdue / Delinquent"
    
    scholarship_val = int(record['input_data'].get('Scholarship holder', 0))
    scholarship_text = "Yes" if scholarship_val == 1 else "No"
    
    student_details_data = [
        [
            Paragraph("Student Name:", body_bold), 
            Paragraph(record.get('student_name', 'N/A') or 'N/A', body_style),
            Paragraph("Student ID:", body_bold), 
            Paragraph(record.get('student_id', 'N/A') or 'N/A', body_style)
        ],
        [
            Paragraph("Enrolled Program:", body_bold), 
            Paragraph(course_name, body_style),
            Paragraph("Age at Enrollment:", body_bold), 
            Paragraph(str(record['input_data'].get('Age at enrollment', 19)), body_style)
        ],
        [
            Paragraph("Gender:", body_bold), 
            Paragraph(gender_text, body_style),
            Paragraph("Assessment Date:", body_bold), 
            Paragraph(record.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M')), body_style)
        ]
    ]
    
    details_table = Table(student_details_data, colWidths=[1.5*inch, 2.0*inch, 1.5*inch, 2.0*inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 15))
    
    # 4. Academic Performance & Indicators
    story.append(Paragraph("Academic & Socioeconomic Indicators", h2_style))
    
    indicators_data = [
        [
            Paragraph("1st Sem Credits Approved:", body_bold),
            Paragraph(str(record['input_data'].get('Curricular units 1st sem (approved)', 0)), body_style),
            Paragraph("1st Sem Avg Grade:", body_bold),
            Paragraph(f"{record['input_data'].get('Curricular units 1st sem (grade)', 0.0):.2f} / 20", body_style)
        ],
        [
            Paragraph("2nd Sem Credits Approved:", body_bold),
            Paragraph(str(record['input_data'].get('Curricular units 2nd sem (approved)', 0)), body_style),
            Paragraph("2nd Sem Avg Grade:", body_bold),
            Paragraph(f"{record['input_data'].get('Curricular units 2nd sem (grade)', 0.0):.2f} / 20", body_style)
        ],
        [
            Paragraph("Outstanding Debt Status:", body_bold),
            Paragraph(debtor_text, body_style),
            Paragraph("Tuition Compliance:", body_bold),
            Paragraph(tuition_text, body_style)
        ],
        [
            Paragraph("Scholarship Recipient:", body_bold),
            Paragraph(scholarship_text, body_style),
            Paragraph("Admission Grade:", body_bold),
            Paragraph(f"{record['input_data'].get('Admission grade', 120.0):.1f} / 200", body_style)
        ]
    ]
    
    indicators_table = Table(indicators_data, colWidths=[1.8*inch, 1.7*inch, 1.8*inch, 1.7*inch])
    indicators_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
    ]))
    story.append(indicators_table)
    story.append(Spacer(1, 15))
    
    # 5. Interventions & Recommendations
    story.append(Paragraph("Tailored Retention Interventions", h2_style))
    
    recs = record.get('recommendations', [])
    if not recs:
        recs = ["No immediate interventions flagged. Student presents low-risk profiles."]
        
    for idx, rec in enumerate(recs):
        story.append(Paragraph(f"&bull; <b>{rec}</b>", rec_item_style))
        story.append(Spacer(1, 4))
        
    story.append(Spacer(1, 20))
    
    # 6. Footer Disclaimer Section
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#94a3b8'),
        alignment=0
    )
    story.append(Paragraph(
        "<b>Disclaimer:</b> This report is generated dynamically by the EduShield predictive analytics model. "
        "Scores and risk classification levels represent probabilistic determinations based on institutional cohorts. "
        "These metrics are designed to assist faculty advisors and should be used alongside direct human counseling reviews.",
        disclaimer_style
    ))
    
    # Build Document
    doc.build(story)
    
    buffer.seek(0)
    return buffer
