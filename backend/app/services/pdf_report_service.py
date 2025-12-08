from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import io

class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.brand_color = colors.HexColor("#0F4C81") # Classic Blue (Resort Genius Brand)
        self.secondary_color = colors.HexColor("#F0F4F8")
        
        # Custom Styles
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.brand_color,
            spaceAfter=20,
            alignment=1 # Center
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=self.brand_color,
            spaceBefore=15,
            spaceAfter=10,
            borderPadding=(0, 0, 5, 0),
            borderColor=self.brand_color,
            borderWidth=0
        ))
        
        self.styles.add(ParagraphStyle(
            name='MetricLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.gray
        ))
        
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        ))

    def _create_metric_card_table(self, data):
        """Creates a row of 3 metric cards"""
        # data list of (Label, Value) tuples
        cell_data = []
        row_labels = []
        row_values = []
        
        for label, value in data:
            row_labels.append(Paragraph(label, self.styles['MetricLabel']))
            row_values.append(Paragraph(value, self.styles['MetricValue']))
            
        return Table([row_labels, row_values], colWidths=[2.2*inch]*3)

    def generate_pdf(self, metrics_data: dict, start_date: str = None, end_date: str = None, hours: int = 24) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        elements = []
        
        # --- Header ---
        elements.append(Paragraph("Resort Genius", self.styles['Normal']))
        elements.append(Paragraph("AI Performance & Financial Report", self.styles['ReportTitle']))
        
        period_str = f"Period: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        if start_date and end_date:
            period_str = f"Period: {start_date} to {end_date}"
        elif hours:
            period_str = f"Period: Last {hours} Hours"
            
        elements.append(Paragraph(period_str, self.styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # --- Executive Summary (Financials) ---
        elements.append(Paragraph("Executive Financial Summary", self.styles['SectionHeader']))
        
        # Calculate ROI/Financials if not pre-calculated (or use passed data)
        # Assuming metrics_data matches the dict returned by MetricsService.get_summary_metrics
        # detailed fields might be in data['cost_breakdown'] etc, but let's assume raw values are passed or we recalculate.
        # Actually, MetricsSummary object has these fields.
        
        total_value = metrics_data.get('total_revenue_potential', 0) + (metrics_data.get('aht_reduction_percent', 0) * 10) # Simplified Mock if missing, but we added logic in service previously
        # Ideally we pass pre-calculated financial dict.
        
        roi_table_data = [
            ["Metric", "Value", "Description"],
            ["Total Value Created", f"${metrics_data.get('total_value_created', 0):,.2f}", "Revenue + Labor Savings"],
            ["Net Benefit", f"${metrics_data.get('net_benefit', 0):,.2f}", "Total Value - Costs"],
            ["ROI Multiplier", f"{metrics_data.get('roi_multiplier', 0):.1f}x", "Return on Spend"]
        ]
        
        t = Table(roi_table_data, colWidths=[2.5*inch, 1.5*inch, 3*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.brand_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, self.secondary_color),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'), # Value column right align
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))
        
        # --- Operational Efficiency ---
        elements.append(Paragraph("Operational Efficiency", self.styles['SectionHeader']))
        
        eff_data = [
            ["Metric", "Result"],
            ["Total Queries", str(metrics_data.get('total_queries', 0))],
            ["Success Rate", f"{metrics_data.get('success_rate', 0):.1f}%"],
            ["Avg Response Time", f"{metrics_data.get('avg_response_time_ms', 0):.0f} ms"],
            ["AHT Equivalent Saved", f"{metrics_data.get('total_aht_saved_hours', 0):.1f} hours"],
            ["FTE Capacity Gained", f"{metrics_data.get('fte_equivalent', 0):.2f} FTEs"]
        ]
        
        t_eff = Table(eff_data, colWidths=[4*inch, 3*inch])
        t_eff.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.secondary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.brand_color),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ]))
        elements.append(t_eff)
        elements.append(Spacer(1, 20))
        
        # --- Revenue & Quality ---
        elements.append(Paragraph("Revenue & Quality Impact", self.styles['SectionHeader']))
        
        req_q_data = [
            # Header
            ["Category", "Metric", "Performance"],
            # Row 1
            ["Revenue", "Potential Generated", f"${metrics_data.get('total_revenue_potential', 0):,.2f}"],
            ["", "Booking Leads", str(metrics_data.get('booking_leads', 0))],
            ["", "Upsell Opportunities", str(metrics_data.get('upsell_opportunities', 0))],
            # Row 2
            ["Quality", "SOP Compliance", f"{metrics_data.get('sop_compliance_rate', 0):.1f}%"],
            ["", "CSAT Score", f"{metrics_data.get('avg_csat', 0):.2f} / 5.0"],
            ["", "Sentiment", "Positive" if metrics_data.get('avg_sentiment', 0) > 0 else "Neutral"]
        ]
        
        t_rev = Table(req_q_data, colWidths=[2*inch, 2.5*inch, 2.5*inch])
        t_rev.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.secondary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.brand_color),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('SPAN', (0, 1), (0, 3)), # Span 'Revenue'
            ('SPAN', (0, 4), (0, 6)), # Span 'Quality'
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(t_rev)
        elements.append(Spacer(1, 30))
        
        # --- Footer ---
        elements.append(Paragraph("Generated by Resort Genius AI | Confidential", 
            ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=8, textColor=colors.gray, alignment=1)))
        
        # Build
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
