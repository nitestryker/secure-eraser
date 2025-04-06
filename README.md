# Secure Eraser

A high-performance cryptographically secure file erasure application with military-grade security standards, custom wiping patterns, advanced verification, detailed reporting capabilities, and comprehensive performance optimizations. Designed for secure data destruction in government, defense, enterprise, and privacy-conscious environments.

## Features

- Multiple secure deletion methods (Standard, DoD 5220.22-M, Gutmann, Paranoid)
- Military-grade security standards (NIST 800-88, HMG IS5, DoD variants, and more)
- Custom wiping pattern support with user-defined patterns
- Complete metadata and filename wiping for total data elimination
- Full file shredding with directory entry sanitization
- Cryptographic verification using multiple hash algorithms
- Detailed reports in JSON, HTML, and PDF formats with visualizations
- Multi-threaded processing with batch file capabilities
- GPU acceleration for faster wiping operations (when available)
- Dynamic resource optimization based on system capabilities
- Pause/resume capability for long-running operations
- Support for files, directories, free space, and entire drives
- Digital report signing
- Comprehensive logging and performance monitoring
- Advanced job management system for handling long operations

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

### Military-Grade Wiping

```bash
# Use NIST SP 800-88 Purge standard for highly sensitive data
python secure_eraser.py --file classified_data.bin --method nist_purge --verify

# Apply UK Government HMG IS5 Enhanced standard
python secure_eraser.py --dir /path/to/sensitive_folder --method hmg_is5_enhanced

# Use NSA/CSS erasure standard for top secret data
python secure_eraser.py --file top_secret.doc --method csc --verify --report-format html

# Department of Defense 7-pass standard with verification
python secure_eraser.py --file military_plans.pdf --method dod_7pass --verify
```

### Custom Pattern Management

```bash
# Create a custom pattern with a specific hex value
python secure_eraser.py --create-pattern corporate_standard --pattern-hex "A5C3F971"

# List all available patterns
python secure_eraser.py --list-patterns

# Use your custom pattern to wipe files
python secure_eraser.py --file confidential.xlsx --custom-pattern corporate_standard

# Delete a custom pattern when no longer needed
python secure_eraser.py --delete-pattern corporate_standard
```

### Metadata Wiping

```bash
# Wipe file content and metadata (filename, timestamps, etc.)
python secure_eraser.py --file secret.doc --wipe-metadata

# Advanced metadata wiping with multiple rename iterations
python secure_eraser.py --file classified.xls --wipe-metadata --rename-iterations 7

# Complete file shredding with metadata sanitization (max security)
python secure_eraser.py --file top_secret.pdf --shred

# Wipe an entire directory with all metadata
python secure_eraser.py --dir /sensitive/folder --wipe-metadata --method dod_7pass

# Secure metadata wiping with verification and reporting
python secure_eraser.py --file confidential.txt --shred --verify --report-format html
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

### Standard Methods
- **Standard**: Basic multi-pass overwrite with random data (default 3 passes)
- **DoD 5220.22-M**: U.S. Department of Defense standard (7 passes)
- **Gutmann**: Peter Gutmann's 35-pass method
- **Paranoid**: Enhanced combined method with additional passes

### Military-Grade Standards
- **NIST SP 800-88 Clear**: National Institute of Standards & Technology Clear standard (1-pass zeros)
- **NIST SP 800-88 Purge**: National Institute of Standards & Technology Purge standard (1-pass ones)
- **DoD 3-pass**: Department of Defense 5220.22-M (3-pass variant)
- **DoD 7-pass**: Department of Defense 5220.22-M (7-pass full standard)
- **HMG IS5 Baseline**: UK Government HMG Infosec Standard 5 baseline method
- **HMG IS5 Enhanced**: UK Government HMG Infosec Standard 5 enhanced method
- **NAVSO P-5239-26**: US Navy NAVSO P-5239-26 standard
- **AFSSI 5020**: Air Force Systems Security Instruction 5020 standard
- **AR 380-19**: Army Regulation 380-19 standard
- **CSC-STD-005-85**: NSA CSS Specification standards

### Custom Patterns
Custom wiping patterns can be created, used, and managed using the following commands:

```bash
# List all available patterns and generators
python secure_eraser.py --list-patterns

# Create a new custom pattern with a hex value
python secure_eraser.py --create-pattern my_pattern --pattern-hex "DEADBEEF"

# Use a custom pattern for wiping
python secure_eraser.py --file sensitive.txt --custom-pattern my_pattern

# Delete a custom pattern
python secure_eraser.py --delete-pattern my_pattern
```

### Metadata Wiping Methods

Secure Eraser provides multiple approaches to wiping file metadata:

- **Basic Metadata Wiping** (`--wipe-metadata`): Overwrites file timestamps, permissions, and attributes
- **Advanced Rename Obfuscation** (`--rename-iterations`): Repeatedly renames the file with random names before deletion
- **Complete File Shredding** (`--shred`): Combines content wiping, metadata sanitization, and directory entry removal
- **Secure Directory Wiping**: Recursively applies metadata wiping to all files in a directory structure

For most sensitive data, combining content wiping with metadata wiping is recommended:
```bash
# Maximum security for classified data
python secure_eraser.py --file top_secret.doc --method gutmann --shred --verify
```

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
- cryptography (for report signing)
- seccomp (optional, for enhanced memory security)

## Recent Changes

### Version 1.2.0 (Latest)
- Added complete metadata wiping functionality with filename sanitization
- Implemented `--shred` option for maximum security file elimination
- Enhanced the military-grade wiping standards with additional options
- Added secure memory handling for sensitive cryptographic operations
- Improved GPU acceleration for faster wiping operations
- Added dynamic resource optimization for better performance
- Created comprehensive documentation for all features
- Refactored code for better modularity and maintainability
- Added new visualization charts in HTML reports
- Enhanced verification with multi-hash algorithm support
- Added advanced job management for better handling of long operations

See [CHANGELOG.md](CHANGELOG.md) for a complete history of changes.

## Documentation

Detailed documentation is available in the [docs/](docs/) directory:

- [Basic Usage](docs/basic_usage.md) - Getting started with Secure Eraser
- [Security Standards](docs/security_standards.md) - Information about wiping methods
- [Metadata Wiping](docs/metadata_wiping.md) - Complete file sanitization
- [Performance Optimization](docs/performance.md) - Tuning for maximum speed
- [Verification Process](docs/verification.md) - Cryptographic verification details
- [Report Formats](docs/reporting.md) - Available report formats and contents
- [Custom Patterns](docs/custom_patterns.md) - Creating and using custom wiping patterns
- [API Reference](docs/api.md) - Using Secure Eraser as a library

## License

MIT License