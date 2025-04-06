# Reporting Features

This guide explains the comprehensive reporting capabilities of Secure Eraser, which allow you to document and visualize the secure erasure process.

## Types of Reports

Secure Eraser supports three report formats:

1. **JSON** - Machine-readable data format
2. **HTML** - Human-readable reports with visualizations
3. **PDF** - Printable documents with formal formatting

## Generating Basic Reports

### JSON Reports

```bash
python secure_eraser.py --file /path/to/file.txt --verify --report-path report.json
```

JSON reports are ideal for:
- Integration with other tools and systems
- Programmatic analysis of results
- Compact storage of operation details

### HTML Reports

```bash
python secure_eraser.py --file /path/to/file.txt --verify --report-format html --report-path report.html
```

HTML reports include:
- Interactive visualizations
- Comprehensive details in a web-friendly format
- Expandable sections for detailed information

### PDF Reports

```bash
python secure_eraser.py --file /path/to/file.txt --verify --report-format pdf --report-path report.pdf
```

PDF reports are suitable for:
- Official documentation
- Printing and archiving
- Compliance documentation
- Formal presentations

## Report Contents

All reports include:

1. **Operation Summary**
   - Date and time of operation
   - Target (file, directory, drive)
   - Wiping method used
   - Number of passes
   - Duration of operation

2. **Wiping Details**
   - Method-specific information
   - Pattern sequences used
   - Pass-by-pass details

3. **Verification Results** (when `--verify` is used)
   - Hash values before wiping
   - Hash values after wiping
   - Verification status
   - Algorithms used

4. **System Information**
   - CPU and memory details
   - Operating system information
   - Storage device information
   - Tool version

5. **Performance Statistics**
   - Throughput (MB/s)
   - Resource utilization
   - Time per pass
   - Operation efficiency metrics

## Enhanced Report Features

### Digital Signing

Add digital signatures to reports for authenticity verification:

```bash
python secure_eraser.py --file /path/to/file.txt --verify --sign-report --report-path report.json
```

Digital signatures ensure the report hasn't been tampered with after generation.

### Custom Report Paths

Specify custom locations for report output:

```bash
python secure_eraser.py --file /path/to/file.txt --verify --report-format html --report-path /path/to/reports/operation_123.html
```

### Visualizations in HTML Reports

HTML reports include several visualizations:

1. **Pattern Visualization**: Visual representation of wiping patterns
2. **Pass Timing Chart**: Graph showing time taken by each pass
3. **Before/After Hash Comparison**: Visual comparison of hash values
4. **Resource Utilization**: CPU, memory, and disk usage during operation
5. **Performance Metrics**: Charts of throughput and efficiency

## Reports for Different Operations

### Directory Wiping Reports

```bash
python secure_eraser.py --dir /path/to/directory --verify --report-format html --report-path directory_report.html
```

Directory reports include:
- Summary of all files processed
- Individual file results
- Statistical overview of the operation

### Drive Wiping Reports

```bash
python secure_eraser.py --drive /path/to/drive --force --verify --report-format pdf --report-path drive_wipe_report.pdf
```

Drive wiping reports include:
- Drive information and specifications
- Sectoring details
- Sampling verification results

### Batch Processing Reports

```bash
python secure_eraser.py --batch file_list.txt --verify --report-format json --report-path batch_report.json
```

Batch reports include:
- Individual results for each file
- Summary statistics
- Success/failure counts

## Report Management

### Automatic Report Naming

If you don't specify a report name, a timestamped name will be generated:

```bash
python secure_eraser.py --file /path/to/file.txt --verify --report-format html
```

This generates a report with a name like `secure_eraser_report_2025-04-06_153045.html`.

### Report Templates

For organizations with custom report requirements, custom report templates can be created:

```bash
python secure_eraser.py --file /path/to/file.txt --verify --report-format html --report-template /path/to/custom_template.html --report-path report.html
```

## Compliance Reporting

For regulatory compliance, specialized reports can be generated:

```bash
python secure_eraser.py --file /path/to/file.txt --method nist_purge --verify --compliance-mode --report-format pdf --report-path compliance_report.pdf
```

Compliance reports include:
- Certification statements
- Reference to applicable standards
- Detailed verification evidence
- Chain of custody information

## Best Practices

1. **Always generate reports** for sensitive data erasure
2. **Use HTML reports** for internal documentation and analysis
3. **Use PDF reports** for formal documentation and compliance
4. **Digitally sign reports** when authenticity is critical
5. **Store reports securely** in accordance with retention policies
6. **Include verification** for comprehensive reports

## Troubleshooting Report Generation

### Report Errors

If report generation fails:

1. Ensure you have proper permissions to write to the target location
2. Verify required libraries are installed:
   - reportlab for PDF reports
   - jinja2 and matplotlib for HTML reports
3. Check disk space for large reports

### Viewing HTML Reports

Open HTML reports in any modern web browser:

```bash
# Linux
xdg-open report.html

# macOS
open report.html

# Windows
start report.html
```

### Converting Reports

Convert between formats using dedicated utilities:

```bash
# Convert JSON to HTML report
python secure_eraser.py --convert-report report.json --output-format html --output-path report.html

# Convert JSON to PDF report
python secure_eraser.py --convert-report report.json --output-format pdf --output-path report.pdf
```

## Related Documentation

- [Verification](verification.md) - Details on the verification process documented in reports
- [Security Standards](security_standards.md) - Understanding the standards referenced in reports
- [Web Interface](web_interface.md) - Viewing reports through the web interface