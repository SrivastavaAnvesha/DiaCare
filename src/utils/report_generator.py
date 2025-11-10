from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import os

class ReportGenerator:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
    def generate_report(self, patient_data, diabetes_result=None, ulcer_result=None):
        # Create unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{patient_data['name'].replace(' ', '_')}_Report_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Add header
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        story.append(Paragraph("DiaCare AI Medical Report", header_style))
        story.append(Spacer(1, 12))
        
        # Add patient information
        story.append(Paragraph("Patient Information", styles['Heading2']))
        patient_info = [
            ["Name:", patient_data['name']],
            ["Age:", str(patient_data['age'])],
            ["Gender:", patient_data['gender']],
            ["Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        ]
        
        t = Table(patient_info, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))
        
        # Add diabetes results if available
        if diabetes_result:
            story.append(Paragraph("Diabetes Risk Assessment", styles['Heading2']))
            risk_level = "High" if diabetes_result['prediction'] == 1 else "Low"
            diabetes_info = [
                ["Risk Level:", risk_level],
                ["Confidence:", f"{diabetes_result['probability']:.1f}%"],
                ["Glucose Level:", str(diabetes_result['glucose'])],
                ["BMI:", str(diabetes_result['bmi'])],
                ["Blood Pressure:", str(diabetes_result['blood_pressure'])]
            ]
            
            t = Table(diabetes_info, colWidths=[2*inch, 4*inch])
            t.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(t)
            story.append(Spacer(1, 20))
        
        # Add ulcer detection results if available
        if ulcer_result and 'image_path' in ulcer_result:
            story.append(Paragraph("Foot Ulcer Detection", styles['Heading2']))
            
            # Add the analyzed image
            if os.path.exists(ulcer_result['image_path']):
                img = Image(ulcer_result['image_path'], width=4*inch, height=3*inch)
                story.append(img)
                story.append(Spacer(1, 12))
            
            ulcer_info = [
                ["Detection Result:", ulcer_result['prediction']],
                ["Confidence:", f"{ulcer_result['probability']:.1f}%"]
            ]
            
            t = Table(ulcer_info, colWidths=[2*inch, 4*inch])
            t.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(t)
        
        # Add footer
        story.append(Spacer(1, 30))
        footer_text = "This report was generated automatically by DiaCare AI system. Please consult with a healthcare professional for proper medical advice."
        story.append(Paragraph(footer_text, styles['Italic']))
        
        # Build PDF
        doc.build(story)
        return filepath
