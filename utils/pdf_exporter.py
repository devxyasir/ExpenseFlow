"""PDF export functionality for Expense Flow - Minimal Design."""
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from utils.helpers import get_export_directory, sanitize_filename
from config import APP_NAME


class PDFExporter:
    """Export company records to PDF with minimal modern design."""
    
    # Design System Colors
    BG_LIGHT = '#f4f4f2'
    BG_DARK = '#0c0c0c'
    ACCENT = '#e85d20'
    TEXT_PRIMARY = '#1a1a1a'
    TEXT_SECONDARY = '#6b6b6b'
    BORDER = '#d4d4d0'
    WHITE = '#ffffff'
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles - Inter font, 400/500 weight only."""
        self.header_style = ParagraphStyle(
            'Header',
            parent=self.styles['Normal'],
            fontSize=18,
            textColor=colors.HexColor(self.TEXT_PRIMARY),
            spaceAfter=0,
            spaceBefore=0,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
        )
        
        self.subheader_style = ParagraphStyle(
            'Subheader',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor(self.TEXT_SECONDARY),
            spaceAfter=0,
            spaceBefore=2,
            alignment=TA_LEFT,
            fontName='Helvetica',
        )
        
        self.company_header_style = ParagraphStyle(
            'CompanyHeader',
            parent=self.styles['Normal'],
            fontSize=13,
            textColor=colors.HexColor(self.TEXT_PRIMARY),
            spaceAfter=0,
            spaceBefore=0,
            fontName='Helvetica-Bold',
        )
        
        self.label_style = ParagraphStyle(
            'Label',
            parent=self.styles['Normal'],
            fontSize=7,
            textColor=colors.HexColor(self.TEXT_SECONDARY),
            spaceAfter=1,
            spaceBefore=0,
            fontName='Helvetica',
        )
        
        self.value_style = ParagraphStyle(
            'Value',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor(self.TEXT_PRIMARY),
            spaceAfter=0,
            spaceBefore=0,
            fontName='Helvetica',
        )
        
        self.section_label_style = ParagraphStyle(
            'SectionLabel',
            parent=self.styles['Normal'],
            fontSize=7,
            textColor=colors.HexColor(self.ACCENT),
            spaceAfter=2,
            spaceBefore=0,
            fontName='Helvetica-Bold',
        )
        
        self.client_name_style = ParagraphStyle(
            'ClientName',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor(self.TEXT_PRIMARY),
            spaceAfter=0,
            spaceBefore=0,
            fontName='Helvetica-Bold',
        )
        
        self.meta_style = ParagraphStyle(
            'Meta',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor(self.TEXT_SECONDARY),
            spaceAfter=0,
            spaceBefore=0,
            fontName='Helvetica',
        )
        
        self.process_name_style = ParagraphStyle(
            'ProcessName',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor(self.TEXT_PRIMARY),
            fontName='Helvetica',
            spaceAfter=0,
            spaceBefore=0,
        )
        
        self.process_amount_style = ParagraphStyle(
            'ProcessAmount',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor(self.TEXT_PRIMARY),
            alignment=TA_RIGHT,
            fontName='Helvetica',
            spaceAfter=0,
            spaceBefore=0,
        )
        
        self.total_label_style = ParagraphStyle(
            'TotalLabel',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor(self.TEXT_SECONDARY),
            fontName='Helvetica',
            spaceAfter=0,
            spaceBefore=0,
        )
        
        self.total_amount_style = ParagraphStyle(
            'TotalAmount',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor(self.ACCENT),
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold',
            spaceAfter=0,
            spaceBefore=0,
        )
        
        self.grand_total_label_style = ParagraphStyle(
            'GrandTotalLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor(self.TEXT_SECONDARY),
            fontName='Helvetica',
            spaceAfter=0,
            spaceBefore=0,
        )
        
        self.grand_total_amount_style = ParagraphStyle(
            'GrandTotalAmount',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor(self.ACCENT),
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold',
            spaceAfter=0,
            spaceBefore=0,
        )
        
        self.footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=7,
            textColor=colors.HexColor(self.TEXT_SECONDARY),
            alignment=TA_CENTER,
            fontName='Helvetica',
            spaceAfter=0,
            spaceBefore=0,
        )
    
    def export_company_records(self, company, records):
        """Export company records to PDF with minimal clean design."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = sanitize_filename(company.name)
        filename = f"{safe_name}_Records_{timestamp}.pdf"
        
        export_dir = get_export_directory()
        filepath = os.path.join(export_dir, filename)
        
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=48,
            bottomMargin=48,
        )
        
        elements = []
        
        # ── HEADER ROW ─────────────────────────────────────────────────
        header_data = [
            [
                Paragraph(APP_NAME, self.header_style),
                Paragraph(
                    f"Company Records Report<br/>"
                    f"<font color='{self.TEXT_SECONDARY}' size='8'>"
                    f"{datetime.now().strftime('%B %d, %Y')}</font>",
                    ParagraphStyle(
                        'HeaderRight',
                        parent=self.styles['Normal'],
                        fontSize=9,
                        textColor=colors.HexColor(self.TEXT_PRIMARY),
                        alignment=TA_RIGHT,
                        fontName='Helvetica',
                        spaceAfter=0,
                        spaceBefore=0,
                    )
                ),
            ]
        ]
        header_table = Table(header_data, colWidths=[3.5*inch, 3.5*inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(header_table)

        elements.append(HRFlowable(
            width="100%",
            thickness=1.5,
            color=colors.HexColor(self.ACCENT),
            spaceAfter=10,
            spaceBefore=0,
        ))

        # ── COMPANY META ROW ───────────────────────────────────────────
        company_meta_data = [
            [
                Paragraph(company.name, self.company_header_style),
                Paragraph(
                    f"<font color='{self.TEXT_SECONDARY}' size='7'>TOTAL CLIENTS</font><br/>"
                    f"{len(records)}",
                    ParagraphStyle(
                        'MetaRight',
                        parent=self.styles['Normal'],
                        fontSize=9,
                        textColor=colors.HexColor(self.TEXT_PRIMARY),
                        alignment=TA_RIGHT,
                        fontName='Helvetica',
                        spaceAfter=0,
                        spaceBefore=0,
                    )
                ),
            ]
        ]
        company_meta_table = Table(company_meta_data, colWidths=[3.5*inch, 3.5*inch])
        company_meta_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(company_meta_table)

        elements.append(HRFlowable(
            width="100%",
            thickness=0.5,
            color=colors.HexColor(self.BORDER),
            spaceAfter=10,
            spaceBefore=0,
        ))

        # ── CLIENT RECORDS ─────────────────────────────────────────────
        grand_total = sum(r.total_amount for r in records)
        
        for i, record in enumerate(records, 1):
            record_elements = []

            # Client header row: index + name | meta info
            meta_parts = []
            if record.phone:
                meta_parts.append(f"Phone: {record.phone}")
            if hasattr(record, 'date') and record.date:
                date_str = record.date.strftime("%b %d, %Y") if hasattr(record.date, 'strftime') else str(record.date)[:10]
                meta_parts.append(f"Date: {date_str}")

            client_header_data = [
                [
                    Paragraph(
                        f"<font color='{self.ACCENT}' size='7'>{i:02d} &nbsp;</font>"
                        f"<b>{record.client_name}</b>",
                        ParagraphStyle(
                            'ClientRow',
                            parent=self.styles['Normal'],
                            fontSize=10,
                            textColor=colors.HexColor(self.TEXT_PRIMARY),
                            fontName='Helvetica',
                            spaceAfter=0,
                            spaceBefore=0,
                        )
                    ),
                    Paragraph(
                        " · ".join(meta_parts) if meta_parts else "",
                        ParagraphStyle(
                            'MetaRight2',
                            parent=self.styles['Normal'],
                            fontSize=8,
                            textColor=colors.HexColor(self.TEXT_SECONDARY),
                            alignment=TA_RIGHT,
                            fontName='Helvetica',
                            spaceAfter=0,
                            spaceBefore=0,
                        )
                    ),
                ]
            ]
            client_header_table = Table(client_header_data, colWidths=[3.5*inch, 3.5*inch])
            client_header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(self.BG_LIGHT)),
            ]))
            record_elements.append(client_header_table)

            # Processes
            if record.processes:
                for j, process in enumerate(record.processes):
                    name = process.get('name', '')
                    amount = process.get('amount', 0)
                    
                    amount_parts = [f"AED {amount:,.2f}"]
                    if process.get('fine'):
                        amount_parts.append(f"Fine AED {process['fine']:,.2f}")
                    if process.get('id_fee'):
                        amount_parts.append(f"ID Fee AED {process['id_fee']:,.2f}")
                    elif process.get('additional'):
                        amount_parts.append(f"+AED {process['additional']:,.2f}")
                    
                    amount_str = "  ·  ".join(amount_parts)
                    is_last = (j == len(record.processes) - 1)

                    process_data = [
                        [
                            Paragraph(name, self.process_name_style),
                            Paragraph(amount_str, self.process_amount_style)
                        ]
                    ]
                    process_table = Table(process_data, colWidths=[4*inch, 3*inch])
                    process_table.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('LEFTPADDING', (0, 0), (0, -1), 10),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                        ('TOPPADDING', (0, 0), (-1, -1), 5),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                        ('LINEBELOW', (0, 0), (-1, -1), 0.5,
                         colors.HexColor(self.ACCENT if is_last else self.BORDER)),
                        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                    ]))
                    record_elements.append(process_table)

            # Client total
            total_data = [
                [
                    Paragraph("Total", self.total_label_style),
                    Paragraph(f"AED {record.total_amount:,.2f}", self.total_amount_style)
                ]
            ]
            total_table = Table(total_data, colWidths=[4*inch, 3*inch])
            total_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (0, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ]))
            record_elements.append(total_table)

            # Wrap all rows in a bordered container
            table_data = [[elem] for elem in record_elements]
            record_container = Table(table_data, colWidths=[7*inch])
            record_container.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor(self.BORDER)),
            ]))

            elements.append(KeepTogether(record_container))
            elements.append(Spacer(1, 8))

        # ── GRAND TOTAL ────────────────────────────────────────────────
        elements.append(Spacer(1, 6))
        grand_total_data = [
            [
                Paragraph("Grand Total", self.grand_total_label_style),
                Paragraph(f"AED {grand_total:,.2f}", self.grand_total_amount_style)
            ]
        ]
        grand_total_table = Table(grand_total_data, colWidths=[4*inch, 3*inch])
        grand_total_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (0, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LINEABOVE', (0, 0), (-1, -1), 1.5, colors.HexColor(self.ACCENT)),
        ]))
        elements.append(grand_total_table)

        # ── FOOTER ─────────────────────────────────────────────────────
        elements.append(Spacer(1, 20))
        elements.append(HRFlowable(
            width="100%",
            thickness=0.5,
            color=colors.HexColor(self.BORDER),
            spaceAfter=6,
            spaceBefore=0,
        ))
        elements.append(Paragraph(
            f"Generated by {APP_NAME} · {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            self.footer_style
        ))
        
        doc.build(elements)
        
        return filepath