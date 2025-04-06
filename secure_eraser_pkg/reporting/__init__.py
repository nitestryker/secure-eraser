"""
Reporting functionality for the Secure Eraser tool.
"""

from typing import Dict, Optional, Any

from secure_eraser_pkg.reporting.json_report import JsonReportGenerator

# Try to import optional report generators
try:
    from secure_eraser_pkg.reporting.html_report import HtmlReportGenerator
    HTML_REPORT_AVAILABLE = True
except ImportError:
    HTML_REPORT_AVAILABLE = False

try:
    from secure_eraser_pkg.reporting.pdf_report import PdfReportGenerator
    PDF_REPORT_AVAILABLE = True
except ImportError:
    PDF_REPORT_AVAILABLE = False


def generate_report(report_format: str, report_data: Dict[str, Any], output_path: str, 
                    signature: Optional[Dict[str, Any]] = None, 
                    system_info: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate a verification report in the specified format.
    
    Args:
        report_format: Format of the report ('json', 'html', or 'pdf')
        report_data: Data to include in the report
        output_path: Path to save the report
        signature: Digital signature information, if available
        system_info: System information to include in the report
        
    Returns:
        Path to the saved report
    """
    report_format = report_format.lower()
    
    if report_format == 'json':
        # JSON reports are always available
        generator = JsonReportGenerator()
        return generator.generate_report(report_data, output_path, signature)
    
    elif report_format == 'html':
        if not HTML_REPORT_AVAILABLE:
            # Fall back to JSON if HTML reports aren't available
            generator = JsonReportGenerator()
            result = generator.generate_report(report_data, output_path, signature)
            raise ImportError("HTML report generation libraries (jinja2, matplotlib) are required. Using JSON format instead.")
        else:
            generator = HtmlReportGenerator()
            return generator.generate_report(report_data, output_path, signature, system_info)
    
    elif report_format == 'pdf':
        if not PDF_REPORT_AVAILABLE:
            # Fall back to JSON if PDF reports aren't available
            generator = JsonReportGenerator()
            result = generator.generate_report(report_data, output_path, signature)
            raise ImportError("PDF report generation libraries (reportlab) are required. Using JSON format instead.")
        else:
            generator = PdfReportGenerator()
            return generator.generate_report(report_data, output_path)
    
    else:
        # Unknown format, fall back to JSON
        generator = JsonReportGenerator()
        result = generator.generate_report(report_data, output_path, signature)
        raise ValueError(f"Unknown report format '{report_format}'. Using JSON format instead.")