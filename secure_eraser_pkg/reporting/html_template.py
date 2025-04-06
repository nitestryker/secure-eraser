"""HTML template for Secure Eraser reports.

This module contains the HTML templates used for generating reports.
Separating the templates from the report generation code makes maintenance easier.
"""

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
                <span>{{ "Yes" if report_data.verification_enabled else "No" }}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Hash Algorithms:</span>
                <span>{% if report_data.hash_algorithms %}{{ ", ".join(report_data.hash_algorithms) }}{% else %}Default{% endif %}</span>
            </div>
        </div>
        
        <!-- Visualizations -->
        {% if charts %}
            {% if charts.summary_chart %}
            <div class="chart-container">
                <h2>Wiping Operations Summary</h2>
                <img class="chart-image" src="data:image/png;base64,{{ charts.summary_chart }}" alt="Wiping Summary Chart">
            </div>
            {% endif %}
            
            {% if charts.size_chart %}
            <div class="chart-container">
                <h2>File Size Distribution</h2>
                <img class="chart-image" src="data:image/png;base64,{{ charts.size_chart }}" alt="File Size Chart">
            </div>
            {% endif %}
            
            {% if charts.verification_chart %}
            <div class="chart-container">
                <h2>Verification Results</h2>
                <img class="chart-image" src="data:image/png;base64,{{ charts.verification_chart }}" alt="Verification Chart">
            </div>
            {% endif %}
            
            {% if charts.performance_chart %}
            <div class="chart-container">
                <h2>Wiping Pass Performance</h2>
                <img class="chart-image" src="data:image/png;base64,{{ charts.performance_chart }}" alt="Performance Chart">
            </div>
            {% endif %}
        {% endif %}
        
        <!-- Wiped Items -->
        <h2>Wiped Items</h2>
        <table>
            <thead>
                <tr>
                    <th>Path</th>
                    <th>Status</th>
                    <th>Size</th>
                    <th>Verified</th>
                </tr>
            </thead>
            <tbody>
                {% for item in report_data.items %}
                <tr>
                    <td>{{ item.path }}</td>
                    <td>{{ item.status }}</td>
                    <td>{{ (item.size / 1024)|round(2) }} KB</td>
                    <td class="{% if item.verification.verified %}status-success{% else %}status-failed{% endif %}">
                        {{ "Yes" if item.verification.verified else "No" }}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <!-- Detailed Hash Information -->
        <h2>Detailed Hash Information</h2>
        {% for item in report_data.items %}
        <h3>{{ item.path }}</h3>
        <table class="hash-table">
            <thead>
                <tr>
                    <th>Algorithm</th>
                    <th>Before Hash</th>
                    <th>After Hash</th>
                    <th>Changed</th>
                </tr>
            </thead>
            <tbody>
                {% if item.verification.before_hashes is mapping %}
                    {% for algo in item.verification.before_hashes.keys() %}
                    <tr>
                        <td>{{ algo }}</td>
                        <td>{{ item.verification.before_hashes[algo][:16] }}...</td>
                        <td>{{ item.verification.after_hashes.get(algo, '')[:16] if item.verification.after_hashes.get(algo) else 'N/A' }}...</td>
                        <td class="{% if item.verification.algorithms_verified.get(algo, False) %}status-success{% else %}status-failed{% endif %}">
                            {{ "Yes" if item.verification.algorithms_verified.get(algo, False) else "No" }}
                        </td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr><td colspan="4">No hash information available</td></tr>
                {% endif %}
            </tbody>
        </table>
        {% endfor %}
        
        <!-- System Information -->
        {% if system_info %}
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
                    <span>{{ system_info.cpu_info.brand }} ({{ system_info.cpu_info.physical_count }} cores, {{ system_info.cpu_info.count }} threads)</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Memory:</span>
                    <span>{{ system_info.memory_total|round(2) }} GB ({{ system_info.memory_available|round(2) }} GB available)</span>
                </div>
            </div>
            
            <!-- Disk Information -->
            <h3>Disk Information</h3>
            <table>
                <thead>
                    <tr>
                        <th>Mount Point</th>
                        <th>Total Size</th>
                        <th>Used</th>
                        <th>Free</th>
                        <th>Usage</th>
                        <th>Type</th>
                    </tr>
                </thead>
                <tbody>
                    {% if system_info.disk_info is mapping %}
                        {% for mount, disk in system_info.disk_info.items() %}
                        <tr>
                            <td>{{ mount }}</td>
                            <td>{{ disk.total|round(2) }} GB</td>
                            <td>{{ disk.used|round(2) }} GB</td>
                            <td>{{ disk.free|round(2) }} GB</td>
                            <td>{{ disk.percent }}%</td>
                            <td>{{ disk.fstype }}</td>
                        </tr>
                        {% endfor %}
                    {% else %}
                        <tr><td colspan="6">No disk information available</td></tr>
                    {% endif %}
                </tbody>
            </table>
        </div>
        {% endif %}
        
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
<head><title>Secure Erasure Report</title></head>
<body>
<h1>Secure Erasure Verification Report</h1>
<p>Report generated on {timestamp}</p>
<p>Wiping Method: {method}</p>
<p>Files wiped: {files_count}</p>
<pre>{json_data}</pre>
</body>
</html>
"""