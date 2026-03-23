from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import io

def extract_text_from_pdf(file_stream):
    try:
        reader = PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def generate_pdf_resume(resume_content, output_stream):
    try:
        doc = SimpleDocTemplate(output_stream, pagesize=letter, topMargin=50, bottomMargin=50)
        styles = getSampleStyleSheet()
        
        # Custom Styles
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=28, alignment=TA_CENTER, spaceAfter=10, fontName='Helvetica-Bold')
        subtitle_style = ParagraphStyle('SubtitleStyle', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER, spaceAfter=5, textColor=colors.grey)
        contact_style = ParagraphStyle('ContactStyle', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER, spaceAfter=20)
        section_header_style = ParagraphStyle('SectionHeader', parent=styles['Heading2'], fontSize=14, spaceBefore=15, spaceAfter=5, fontName='Helvetica-Bold', leftIndent=0)
        body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=10)

        story = []
        lines = resume_content.split('\n')
        
        # Simple parser to find header info
        for i, line in enumerate(lines):
            line = line.strip()
            if not line: continue
            
            # First line is likely the name
            if i == 0 or "NAME:" in line.upper():
                name = line.replace("NAME:", "").strip()
                story.append(Paragraph(name.upper(), title_style))
                continue
            
            # Second line is likely the title
            if "TITLE:" in line.upper():
                title = line.replace("TITLE:", "").strip()
                story.append(Paragraph(title, subtitle_style))
                continue

            # Contact line
            if "CONTACT:" in line.upper():
                contact = line.replace("CONTACT:", "").strip()
                story.append(Paragraph(contact, contact_style))
                story.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=0, spaceAfter=10))
                continue

            # Section Headers (All caps lines)
            if line.isupper() and len(line) < 30:
                story.append(Paragraph(line, section_header_style))
                story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey, spaceBefore=2, spaceAfter=10))
            else:
                # Normal body text
                story.append(Paragraph(line, body_style))

        doc.build(story)
        return True
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return False
