# Secure Eraser

A cryptographically secure file erasure application with advanced verification, reporting capabilities, and performance optimizations.

## Features

- Multiple secure deletion methods (Standard, DoD 5220.22-M, Gutmann, Paranoid)
- Cryptographic verification using multiple hash algorithms
- Detailed reports in JSON, HTML, and PDF formats with visualizations
- Multi-threaded processing with batch file capabilities
- GPU acceleration for faster wiping operations (when available)
- Dynamic resource optimization based on system capabilities
- Pause/resume capability for long-running operations
- Support for files, directories, free space, and entire drives
- Digital report signing
- Comprehensive logging and performance monitoring

## Installation

### Using pip

```bash
pip install secure-eraser
```

### From source

```bash
git clone https://github.com/username/secure-eraser.git
cd secure-eraser
pip install -e .
```

## Usage

### Basic Usage

```bash
# Securely delete a file
python secure_eraser.py --file /path/to/file.txt

# Securely delete a directory
python secure_eraser.py --dir /path/to/directory

# Wipe free space
python secure_eraser.py --freespace /path/to/drive

# Wipe an entire drive (DANGER!)
python secure_eraser.py --drive /path/to/drive --force
```

### Advanced Options

```bash
# Use DoD 5220.22-M wiping method with 7 passes
python secure_eraser.py --file /path/to/file.txt --method dod --passes 7

# Enable cryptographic verification
python secure_eraser.py --file /path/to/file.txt --verify

# Specify hash algorithms for verification
python secure_eraser.py --file /path/to/file.txt --verify --hash-algorithms sha256,sha3_256

# Generate HTML report with visualizations
python secure_eraser.py --file /path/to/file.txt --verify --report-format html --report-path report.html

# Digitally sign verification report
python secure_eraser.py --file /path/to/file.txt --verify --sign-report --report-path report.json

# Verbose logging to file
python secure_eraser.py --file /path/to/file.txt --verbose --log-file eraser.log
```

### Performance Optimization

```bash
# Process multiple files from a batch file with GPU acceleration
python secure_eraser.py --batch file_list.txt --gpu --workers 4

# Enable dynamic resource optimization for system-aware performance
python secure_eraser.py --file large_file.bin --optimize-resources

# Set custom chunk size for memory efficiency
python secure_eraser.py --file huge_file.bin --chunk-size 50

# Resume a paused operation
python secure_eraser.py --job-id abc123def456

# List all available jobs
python secure_eraser.py --list-jobs

# Cancel a running job
python secure_eraser.py --cancel-job abc123def456
```

## Wiping Methods

- **Standard**: Basic multi-pass overwrite with random data (default 3 passes)
- **DoD 5220.22-M**: U.S. Department of Defense standard (7 passes)
- **Gutmann**: Peter Gutmann's 35-pass method
- **Paranoid**: Enhanced combined method with additional passes

## Verification

When enabled with `--verify`, Secure Eraser performs cryptographic verification:

1. Computes hash values of the file before wiping
2. Overwrites the file using the specified method and passes
3. Computes hash values after wiping
4. Verifies that the hash values have changed (indicating successful wiping)

## Reports

Verification reports can be generated in multiple formats:

- **JSON**: Machine-readable data (default)
- **HTML**: Human-readable report with charts and visualizations
- **PDF**: Printable document with verification details

Reports include:
- Wiping method and passes
- Hash values before and after wiping
- Verification status
- System information
- Performance statistics
- Digital signature (if enabled)

## Requirements

- Python 3.9+
- reportlab (for PDF reports)
- matplotlib (for HTML report visualizations)
- jinja2 (for HTML templates)
- py-cpuinfo (for system information)
- psutil (for system monitoring)
- pycuda (optional, for GPU acceleration)
- numpy (for data processing and GPU acceleration)

## License

MIT License