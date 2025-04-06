"""
JSON report generation for the Secure Eraser tool.
"""

import json
import datetime
import logging
from typing import Dict, Optional, Any


class JsonReportGenerator:
    """
    Generates JSON verification reports for secure wiping operations.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the JSON report generator.
        
        Args:
            logger: Logger instance to use (if None, a new one will be created)
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def generate_report(self, report_data: Dict[str, Any], output_path: Optional[str] = None,
                        signature: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a JSON verification report.
        
        Args:
            report_data: Data to include in the report
            output_path: Path to save the report (if None, returns the report as a string)
            signature: Digital signature information, if available
            
        Returns:
            Path to the saved report, or the report as a string if output_path is None
        """
        try:
            # Create report structure
            full_report = {
                "verification_report": {
                    "title": "Secure Erasure Verification Report",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "wiping_method": report_data.get("wiping_method", "standard"),
                    "passes": report_data.get("passes", 0),
                    "verification_enabled": report_data.get("verification_enabled", False),
                    "algorithms_used": report_data.get("hash_algorithms", []),
                    "system_info": report_data.get("system_info", {}),
                    "items": report_data.get("wiped_items", []),
                    "summary": {
                        "files_wiped": len(report_data.get("wiped_items", [])),
                        "total_bytes_wiped": sum(item.get("size", 0) for item in report_data.get("wiped_items", [])),
                        "verified_items": sum(1 for item in report_data.get("wiped_items", []) 
                                             if item.get("verification", {}).get("verified", False))
                    }
                }
            }
            
            # Add signature if available
            if signature:
                full_report["digital_signature"] = signature
            
            # Convert to JSON string with pretty formatting
            json_str = json.dumps(full_report, indent=2)
            
            # Save to file if output path provided
            if output_path:
                with open(output_path, 'w') as f:
                    f.write(json_str)
                self.logger.info(f"JSON report saved to {output_path}")
                return output_path
            
            # Otherwise return as string
            return json_str
            
        except Exception as e:
            self.logger.error(f"Error generating JSON report: {e}")
            raise