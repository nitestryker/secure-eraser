"""
PDF report generation for the Secure Eraser tool.
"""

import datetime
import logging
from typing import Dict, Optional, Any

# Check if reportlab is available for PDF generation
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class PdfReportGenerator:
    """
    Generates PDF verification reports for secure wiping operations.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the PDF report generator.
        
        Args:
            logger: Logger instance to use (if None, a new one will be created)
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def generate_report(self, report_data: Dict[str, Any], output_path: str) -> str:
        """
        Generate a PDF verification report.
        
        Args:
            report_data: Data to include in the report
            output_path: Path to save the report
            
        Returns:
            Path to the saved report
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required for PDF report generation")
            
        try:
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []
            
            # Title
            title_style = styles["Heading1"]
            elements.append(Paragraph("Secure Erasure Verification Report", title_style))
            elements.append(Spacer(1, 12))
            
            # Summary information
            summary_style = styles["Normal"]
            elements.append(Paragraph(f"<b>Date:</b> {report_data.get('timestamp', 'Unknown')[:19].replace('T', ' ')}", summary_style))
            elements.append(Paragraph(f"<b>Wiping Method:</b> {report_data.get('wiping_method', 'standard').upper()}", summary_style))
            elements.append(Paragraph(f"<b>Passes:</b> {report_data.get('passes', 0)}", summary_style))
            elements.append(Paragraph(f"<b>Verification Enabled:</b> {report_data.get('verification_enabled', False)}", summary_style))
            
            hash_algorithms = report_data.get('hash_algorithms', [])
            elements.append(Paragraph(f"<b>Hash Algorithms:</b> {', '.join(hash_algorithms)}", summary_style))
            
            # System info if available
            system_info = report_data.get('system_info', {})
            if system_info:
                elements.append(Paragraph(f"<b>System:</b> {system_info.get('platform', 'Unknown')} {system_info.get('platform_version', '')}", summary_style))
            elements.append(Spacer(1, 20))
            
            # Table of wiped items
            elements.append(Paragraph("Wiped Items", styles["Heading2"]))
            elements.append(Spacer(1, 12))
            
            items = report_data.get('items', [])
            
            # Create table data
            table_data = [["File Name", "Status", "Size", "Verified"]]
            
            for item in items:
                file_name = item.get('file_name', 'Unknown')
                status = item.get('status', 'Unknown')
                size = f"{item.get('size', 0) / 1024:.2f} KB" if item.get('size', 0) > 0 else "0 KB"
                
                verification = item.get('verification', {})
                verified = "Yes" if verification.get('verified', False) else "No"
                
                table_data.append([file_name, status, size, verified])
                
            # Create table
            if len(table_data) > 1:  # Only create table if we have items
                table = Table(table_data, colWidths=[200, 100, 100, 80])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                
                elements.append(table)
                elements.append(Spacer(1, 20))
            else:
                elements.append(Paragraph("No items were wiped in this operation.", summary_style))
                elements.append(Spacer(1, 20))
            
            # Detailed hash information for each item
            if items:
                elements.append(Paragraph("Detailed Hash Information", styles["Heading2"]))
                elements.append(Spacer(1, 12))
                
                for item in items:
                    elements.append(Paragraph(f"<b>File:</b> {item.get('path', 'Unknown')}", summary_style))
                    
                    verification = item.get('verification', {})
                    before_hashes = verification.get('before_hashes', {})
                    
                    if before_hashes:
                        hash_table_data = [["Algorithm", "Before Hash", "After Hash", "Changed"]]
                        
                        for algo in before_hashes.keys():
                            before_hash = before_hashes.get(algo, 'N/A')
                            after_hash = verification.get('after_hashes', {}).get(algo, 'N/A')
                            
                            # Display only a portion of the hash for readability
                            if len(before_hash) > 16:
                                before_hash = before_hash[:16] + "..."
                            if len(after_hash) > 16:
                                after_hash = after_hash[:16] + "..."
                                
                            changed = "Yes" if verification.get('algorithms_verified', {}).get(algo, False) else "No"
                            hash_table_data.append([algo, before_hash, after_hash, changed])
                            
                        hash_table = Table(hash_table_data, colWidths=[100, 150, 150, 60])
                        hash_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ]))
                        
                        elements.append(hash_table)
                    else:
                        elements.append(Paragraph("No hash information available", summary_style))
                        
                    elements.append(Spacer(1, 12))
            
            # Build PDF
            doc.build(elements)
            self.logger.info(f"PDF report saved to {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error generating PDF report: {e}")
            raise