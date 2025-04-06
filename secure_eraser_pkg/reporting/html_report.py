"""
HTML report generation for the Secure Eraser tool.
"""
import json
import logging
import datetime
import sys
from io import BytesIO
import base64
from typing import Dict, Any, Optional, List, Union, Tuple

# Try to import visualization libraries, but handle failure gracefully
HTML_REPORT_AVAILABLE = True
try:
    import jinja2
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
except ImportError:
    HTML_REPORT_AVAILABLE = False


# HTML Template for reports
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Erasure Verification Report</title>
    <style>
        :root {
            --primary-color: #007bff;
            --secondary-color: #6c757d;
            --success-color: #28a745;
            --danger-color: #dc3545;
            --light-color: #f8f9fa;
            --dark-color: #343a40;
        }
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
            background-color: #f4f4f4;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            border-radius: 5px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }
        .verification-info {
            display: flex;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }
        .info-item {
            flex: 1;
            min-width: 250px;
            margin-bottom: 15px;
        }
        .info-label {
            font-weight: bold;
            margin-right: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        table, th, td {
            border: 1px solid #ddd;
        }
        th, td {
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: var(--primary-color);
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .status-success {
            color: var(--success-color);
            font-weight: bold;
        }
        .status-failed {
            color: var(--danger-color);
            font-weight: bold;
        }
        .signature-section {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }
        .hash-table {
            font-size: 0.9em;
        }
        .chart-container {
            margin: 20px 0;
            text-align: center;
        }
        .chart-image {
            max-width: 100%;
            height: auto;
        }
        .system-info {
            margin-top: 30px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        .footer {
            margin-top: 40px;
            text-align: center;
            font-size: 0.8em;
            color: #777;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Secure Erasure Verification Report</h1>
            <p>Report generated on {{ report_data.timestamp }}</p>
        </div>
        
        <div class="verification-info">
            <div class="info-item">
                <span class="info-label">Wiping Method:</span>
                <span>{{ report_data.wiping_method.upper() }}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Number of Passes:</span>
                <span>{{ report_data.passes }}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Verification Enabled:</span>
                <span>{{ report_data.verification_enabled }}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Hash Algorithms:</span>
                <span>{{ ', '.join(report_data.hash_algorithms) }}</span>
            </div>
        </div>
        
        <!-- Visualization -->
        {% if charts and charts.summary_chart %}
        <div class="chart-container">
            <h2>Wiping Operations Summary</h2>
            <img class="chart-image" src="data:image/png;base64,{{ charts.summary_chart }}" alt="Wiping Summary Chart">
        </div>
        {% endif %}
        
        {% if charts and charts.size_chart %}
        <div class="chart-container">
            <h2>File Size Distribution</h2>
            <img class="chart-image" src="data:image/png;base64,{{ charts.size_chart }}" alt="File Size Distribution">
        </div>
        {% endif %}
        
        {% if charts and charts.verification_chart %}
        <div class="chart-container">
            <h2>Verification Results</h2>
            <img class="chart-image" src="data:image/png;base64,{{ charts.verification_chart }}" alt="Verification Results">
        </div>
        {% endif %}
        
        {% if charts and charts.performance_chart %}
        <div class="chart-container">
            <h2>Wiping Performance</h2>
            <img class="chart-image" src="data:image/png;base64,{{ charts.performance_chart }}" alt="Wiping Performance">
        </div>
        {% endif %}
        
        <h2>Wiped Items</h2>
        <table>
            <thead>
                <tr>
                    <th>File Name</th>
                    <th>Status</th>
                    <th>Size</th>
                    <th>Verified</th>
                </tr>
            </thead>
            <tbody>
                {% for item in report_data.items %}
                <tr>
                    <td>{{ item.file_name }}</td>
                    <td>{{ item.status }}</td>
                    <td>{{ (item.size / 1024)|round(2) }} KB</td>
                    <td class="{% if item.verification.verified %}status-success{% else %}status-failed{% endif %}">
                        {{ "Yes" if item.verification.verified else "No" }}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <!-- System Information -->
        <div class="system-info">
            <h2>System Information</h2>
            <div class="verification-info">
                <div class="info-item">
                    <span class="info-label">Hostname:</span>
                    <span>{{ system_info.hostname }}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Platform:</span>
                    <span>{{ system_info.platform }} {{ system_info.platform_version }}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">CPU:</span>
                    <span>{{ system_info.cpu_info.brand }} ({{ system_info.cpu_info.count }} cores)</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Memory:</span>
                    <span>{{ system_info.memory_total|round(2) }} GB total / {{ system_info.memory_available|round(2) }} GB available</span>
                </div>
            </div>
        </div>
        
        <!-- Digital Signature if available -->
        {% if signature %}
        <div class="signature-section">
            <h2>Digital Signature</h2>
            <div class="info-item">
                <span class="info-label">Signature Algorithm:</span>
                <span>{{ signature.algorithm }}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Signature Date:</span>
                <span>{{ signature.timestamp }}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Signature Value:</span>
                <span style="word-break: break-all;">{{ signature.value }}</span>
            </div>
        </div>
        {% endif %}
        
        <div class="footer">
            <p>Generated with Secure Eraser v1.0.0</p>
            <p>© {{ report_data.timestamp[:4] }} Secure Eraser</p>
        </div>
    </div>
</body>
</html>
"""

# Simple fallback HTML template for when visualization libraries aren't available
FALLBACK_HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>Secure Erasure Report</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }
        h1 { color: #333; }
        pre { background-color: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>Secure Erasure Verification Report</h1>
    <p>Report generated on {timestamp}</p>
    <p>Wiping Method: {method}</p>
    <p>Files wiped: {files_count}</p>
    <pre>{json_data}</pre>
</body>
</html>
"""


class HtmlReportGenerator:
    """
    Generates HTML verification reports for secure wiping operations.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the HTML report generator.
        
        Args:
            logger: Logger instance to use (if None, a new one will be created)
        """
        self.logger = logger or logging.getLogger(__name__)
        
    def _prepare_data_for_json(self, data: Any) -> Any:
        """
        Recursively prepare data for JSON serialization by converting datetime objects to strings.
        
        Args:
            data: Data to prepare for JSON serialization
            
        Returns:
            JSON-serializable data
        """
        if isinstance(data, dict):
            return {k: self._prepare_data_for_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._prepare_data_for_json(item) for item in data]
        elif isinstance(data, tuple):
            return tuple(self._prepare_data_for_json(item) for item in data)
        elif isinstance(data, datetime.datetime):
            return data.isoformat()
        elif isinstance(data, (int, float, str, bool, type(None))):
            return data
        else:
            return str(data)
    
    def generate_report(self, report_data: Dict[str, Any], output_path: str,
                        signature: Optional[Dict[str, Any]] = None,
                        system_info: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate an HTML verification report.
        
        Args:
            report_data: Data to include in the report
            output_path: Path to save the report
            signature: Digital signature information, if available
            system_info: System information to include in the report
            
        Returns:
            Path to the saved report
        """
        if not HTML_REPORT_AVAILABLE:
            return self._generate_fallback_html(report_data, output_path)
            
        try:
            self.logger.info("Generating HTML report with visualizations")
            
            # Generate charts if possible
            charts = self._generate_performance_charts(report_data)
            
            # Debug the report_data structure
            self.logger.debug(f"Report data items type: {type(report_data.get('items', []))}")
            
            # Add safety check for items - ensure it's iterable
            if not isinstance(report_data.get('items', []), (list, tuple)) or not report_data.get('items'):
                report_data['items'] = []
                self.logger.warning("No items found in report data, using empty list")
            
            # Create a simpler template with more basic jinja2 constructs
            try:
                env = jinja2.Environment(autoescape=True)
                template = env.from_string(HTML_TEMPLATE)
                
                # Process data to ensure it's serializable
                report_data_safe = self._prepare_data_for_json(report_data)
                system_info_safe = self._prepare_data_for_json(system_info or {})
                signature_safe = self._prepare_data_for_json(signature) if signature else None
                
                # The key issue appears to be a conflict between dict.items() method and data['items']
                # Let's create a modified template by renaming items references
                modified_template = HTML_TEMPLATE
                
                # Replace all instances of report_data.items with report_data.items_list in the template
                # This avoids the conflict completely
                modified_template = modified_template.replace("report_data.items", "report_data.items_list")
                template = env.from_string(modified_template)
                
                # Create a modified data dictionary with items renamed to items_list
                if 'items' in report_data_safe:
                    # Save the original items list
                    items_data = report_data_safe.pop('items', [])
                    # If we have real items in the original data, use those
                    if isinstance(report_data.get('items'), list):
                        report_data_safe['items_list'] = report_data.get('items')
                    # Otherwise use the data we saved
                    elif isinstance(items_data, list):
                        report_data_safe['items_list'] = items_data
                    else:
                        report_data_safe['items_list'] = []
                    
                    # Keep items in the dict for backward compatibility with other code
                    report_data_safe['items'] = report_data_safe['items_list']
                
                # Create a context dictionary with safer defaults for items that might be missing
                context = {
                    'report_data': report_data_safe,
                    'system_info': system_info_safe,
                    'charts': charts or {},
                    'signature': signature_safe
                }
                html_content = template.render(**context)
            except Exception as e:
                self.logger.error(f"Template rendering error: {e}")
                return self._generate_fallback_html(report_data, output_path)
            
            # Write HTML file
            with open(output_path, 'w') as f:
                f.write(html_content)
                
            self.logger.info(f"HTML report with {len(charts)} charts generated successfully")
            return output_path
                
        except Exception as e:
            self.logger.error(f"Error generating HTML report: {e}")
            return self._generate_fallback_html(report_data, output_path)
            
    def _generate_fallback_html(self, report_data: Dict[str, Any], output_path: str) -> str:
        """
        Generate a simple fallback HTML report when visualization fails.
        
        Args:
            report_data: Data to include in the report
            output_path: Path to save the report
            
        Returns:
            Path to the saved report
        """
        try:
            # Create a very basic HTML report as fallback
            # Convert any datetime objects to strings
            report_data_safe = self._prepare_data_for_json(report_data)
            
            html_content = FALLBACK_HTML_TEMPLATE.format(
                timestamp=str(report_data.get('timestamp', datetime.datetime.now().isoformat())),
                method=str(report_data.get('wiping_method', 'standard')).upper(),
                files_count=len(report_data.get('items', [])),
                json_data=json.dumps(report_data_safe, indent=2)
            )
            
            # Write HTML file
            with open(output_path, 'w') as f:
                f.write(html_content)
                
            self.logger.info("Fallback HTML report generated successfully")
            return output_path
        except Exception as e:
            self.logger.error(f"Error generating fallback HTML report: {e}")
            raise
        
    def _generate_performance_charts(self, report_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate charts for performance visualization.
        
        Args:
            report_data: Report data containing performance information
            
        Returns:
            Dictionary mapping chart names to base64-encoded chart images
        """
        if not HTML_REPORT_AVAILABLE:
            return {}
            
        # If matplotlib is not available, return empty dictionary
        if 'matplotlib.pyplot' not in sys.modules:
            self.logger.warning("Matplotlib not available, skipping chart generation")
            return {}
            
        # Import matplotlib within the function to handle module import issues
        try:
            import matplotlib.pyplot as plt
            from matplotlib import ticker
        except ImportError:
            self.logger.warning("Failed to import matplotlib, skipping chart generation")
            return {}
            
        charts = {}
        
        try:
            # Summary chart showing operation statistics
            items = report_data.get('items', [])
            
            # Make sure items is iterable and not empty
            if not items or not isinstance(items, (list, tuple)):
                return {}
                
            plt.figure(figsize=(10, 6))
            
            # Count operation types
            operation_types = {}
            file_sizes = []
            verified_count = 0
            
            for item in items:
                # Make sure item is a dictionary
                if not isinstance(item, dict):
                    continue
                    
                status = item.get('status', '').lower()
                op_type = "File" if "file" in status else "Directory" if "directory" in status else "Other"
                
                if op_type not in operation_types:
                    operation_types[op_type] = 0
                operation_types[op_type] += 1
                
                # Track file sizes and verification status
                size = item.get('size', 0)
                if size > 0:
                    file_sizes.append(size / (1024*1024))  # Convert to MB
                
                verification = item.get('verification', {})
                if isinstance(verification, dict) and verification.get('verified', False):
                    verified_count += 1
            
            # Create summary bar chart
            if operation_types:
                labels = list(operation_types.keys())
                values = list(operation_types.values())
                
                plt.bar(labels, values, color=['#3498db', '#2ecc71', '#9b59b6'])
                plt.title('Operation Types')
                plt.ylabel('Count')
                plt.grid(axis='y', alpha=0.3)
                
                # Save chart to bytes buffer
                buffer = BytesIO()
                plt.tight_layout()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                
                # Convert to base64 for embedding in HTML
                charts["summary_chart"] = base64.b64encode(buffer.getvalue()).decode('utf-8')
                plt.close()
            
                # Create a chart for file sizes if we have size data
                if file_sizes:
                    plt.figure(figsize=(10, 6))
                    plt.hist(file_sizes, bins=10, color='#3498db')
                    plt.title('File Size Distribution')
                    plt.xlabel('Size (MB)')
                    plt.ylabel('Count')
                    plt.grid(axis='y', alpha=0.3)
                    
                    # Save chart to bytes buffer
                    buffer = BytesIO()
                    plt.tight_layout()
                    plt.savefig(buffer, format='png')
                    buffer.seek(0)
                    
                    # Convert to base64 for embedding in HTML
                    charts["size_chart"] = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    plt.close()
            
                # Create a chart for verification results if verification was enabled
                if report_data.get('verification_enabled', False) and items:
                    plt.figure(figsize=(8, 8))
                    
                    verified = verified_count
                    not_verified = len(items) - verified_count
                    
                    plt.pie([verified, not_verified], 
                            labels=['Verified', 'Not Verified'],
                            autopct='%1.1f%%',
                            colors=['#2ecc71', '#e74c3c'],
                            startangle=90)
                    plt.axis('equal')
                    plt.title('Verification Results')
                    
                    # Save chart to bytes buffer
                    buffer = BytesIO()
                    plt.tight_layout()
                    plt.savefig(buffer, format='png')
                    buffer.seek(0)
                    
                    # Convert to base64 for embedding in HTML
                    charts["verification_chart"] = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    plt.close()
        
            # Performance chart if we have performance data
            pass_durations = report_data.get('performance_stats', {}).get('pass_durations', [])
            if pass_durations:
                plt.figure(figsize=(10, 6))
                
                x = list(range(1, len(pass_durations) + 1))
                y = pass_durations
                
                plt.plot(x, y, marker='o', linestyle='-', color='#3498db')
                plt.title('Wiping Pass Durations')
                plt.xlabel('Pass Number')
                plt.ylabel('Duration (seconds)')
                plt.grid(True, alpha=0.3)
                
                # Save chart to bytes buffer
                buffer = BytesIO()
                plt.tight_layout()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                
                # Convert to base64 for embedding in HTML
                charts["performance_chart"] = base64.b64encode(buffer.getvalue()).decode('utf-8')
                plt.close()
                
        except Exception as e:
            self.logger.error(f"Error generating charts: {e}")
            
        return charts
