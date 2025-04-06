# Basic Usage

This guide explains the fundamental operations of Secure Eraser, covering file, directory, and drive wiping along with common options and configurations.

## Installation and Requirements

Before using Secure Eraser, ensure you have:

1. Python 3.9 or higher installed
2. Required dependencies installed:
   ```bash
   pip install psutil py-cpuinfo reportlab jinja2 matplotlib
   ```
3. Optional dependencies for advanced features:
   ```bash
   # For GPU acceleration
   pip install pycuda numpy
   
   # For digital signing
   pip install cryptography
   ```

## Command Structure

Secure Eraser uses the following general command structure:

```bash
python secure_eraser.py [TARGET OPTIONS] [WIPING METHOD] [ADDITIONAL OPTIONS]
```

For example:
```bash
python secure_eraser.py --file document.txt --method dod_3pass --verify
```

## Basic Operations

### Wiping a Single File

To securely erase a single file:

```bash
python secure_eraser.py --file /path/to/file.txt
```

This uses the default wiping method (NIST 800-88 Clear).

### Wiping a Directory

To securely erase all files in a directory:

```bash
python secure_eraser.py --dir /path/to/directory
```

This recursively wipes all files in the directory and its subdirectories.

### Wiping Free Space

To wipe only the free space on a drive (leaving existing files intact):

```bash
python secure_eraser.py --free-space /path/to/drive
```

This creates temporary files that fill the available space, wipes them, and then removes them.

### Wiping an Entire Drive

To wipe an entire drive or partition (requires administrative privileges):

```bash
python secure_eraser.py --drive /dev/sdX --force
```

**Warning**: This permanently destroys all data on the drive. The `--force` flag is required as a safety measure.

## Wiping Methods

### Choosing a Wiping Method

Specify a wiping method with the `--method` option:

```bash
python secure_eraser.py --file /path/to/file.txt --method dod_3pass
```

Available standard methods include:
- `zero`: Single pass of zeros (fastest, minimal security)
- `random`: Overwrite with random data
- `nist_clear`: NIST 800-88 Clear method (default)
- `nist_purge`: NIST 800-88 Purge method (more secure)
- `dod_3pass`: DoD 5220.22-M 3-pass method
- `dod_7pass`: DoD 5220.22-M ECE 7-pass method
- `gutmann`: Peter Gutmann's 35-pass method (most secure, very slow)
- `schneier`: Bruce Schneier's 7-pass method
- `hmg_enhanced`: HMG IS5 Enhanced method
- `hmg_higher`: HMG IS5 Higher standard method

### Specifying Pass Count

For methods that support it, specify the number of passes:

```bash
python secure_eraser.py --file /path/to/file.txt --method random --passes 7
```

## Verification

### Basic Verification

Enable verification to confirm successful wiping:

```bash
python secure_eraser.py --file /path/to/file.txt --verify
```

### Verification Level

Specify the verification thoroughness:

```bash
python secure_eraser.py --file /path/to/file.txt --verify --verification-level full
```

Available levels:
- `sample`: Quick verification of representative samples (default for large files)
- `standard`: Regular verification (default for normal files)
- `full`: Comprehensive verification (slowest, most secure)

## Reporting

### Generating Reports

Create a report of the wiping operation:

```bash
python secure_eraser.py --file /path/to/file.txt --verify --report-format html --report-path report.html
```

Available report formats:
- `json`: Machine-readable JSON format
- `html`: Interactive HTML report with visualizations
- `pdf`: Printable PDF document

### Automatic Report Naming

If you don't specify a report path, a timestamped name will be generated:

```bash
python secure_eraser.py --file /path/to/file.txt --verify --report-format html
```

## Performance Options

### Multi-threaded Processing

Enable parallel processing with multiple threads:

```bash
python secure_eraser.py --file /path/to/large_file.bin --workers 4
```

Use `--workers auto` to automatically determine the optimal number of threads.

### GPU Acceleration

If you have compatible NVIDIA GPU hardware, enable GPU acceleration:

```bash
python secure_eraser.py --file /path/to/large_file.bin --gpu
```

### Resource Optimization

Optimize resource usage based on system load:

```bash
python secure_eraser.py --file /path/to/file.txt --optimize-resources
```

### Chunk Size

Specify memory chunk size (in MB) for processing large files:

```bash
python secure_eraser.py --file /path/to/huge_file.bin --chunk-size 50
```

## Batch Operations

### Processing Multiple Files

Wipe multiple files listed in a text file:

```bash
python secure_eraser.py --batch file_list.txt
```

Where `file_list.txt` contains one file path per line.

### Creating File Lists

Generate a list of files matching a pattern:

```bash
# On Linux/macOS
find /path/to/search -name "*.doc" > documents_list.txt

# On Windows (PowerShell)
Get-ChildItem -Path C:\path\to\search -Filter *.doc -Recurse | Select-Object FullName > documents_list.txt

# Then use the generated list
python secure_eraser.py --batch documents_list.txt
```

## Common Options

### Verbose Output

Get detailed information during operation:

```bash
python secure_eraser.py --file /path/to/file.txt --verbose
```

### Quiet Mode

Suppress all output except errors:

```bash
python secure_eraser.py --file /path/to/file.txt --quiet
```

### Force Operation

Override safety checks:

```bash
python secure_eraser.py --drive /dev/sdX --force
```

### Dry Run

Simulate the operation without actually wiping anything:

```bash
python secure_eraser.py --file /path/to/file.txt --dry-run
```

## Special Use Cases

### Wiping Specific File Types

Wipe all files of a specific type in a directory:

```bash
# First create a list of files
find /path/to/search -name "*.log" > logs_list.txt

# Then wipe them
python secure_eraser.py --batch logs_list.txt
```

### Excluding Files or Directories

Exclude specific patterns when wiping a directory:

```bash
python secure_eraser.py --dir /path/to/directory --exclude "*.jpg,*.png,backup/*"
```

### Working with Large Files

For very large files, optimize memory usage:

```bash
python secure_eraser.py --file /path/to/huge_file --chunk-size 10 --streaming-mode
```

### Metadata and Filename Wiping

To wipe a file's contents along with its metadata and filename:

```bash
python secure_eraser.py --file /path/to/sensitive_file.txt --wipe-metadata
```

For complete file shredding (contents and all traces):

```bash
python secure_eraser.py --file /path/to/sensitive_file.txt --shred
```

## Security Best Practices

1. **Always verify** wiping operations with `--verify`
2. **Match the method** to the sensitivity of the data
3. **Use strong methods** for sensitive information
4. **Generate reports** for compliance and auditing
5. **Check verification results** to ensure complete wiping
6. **Use appropriate privileges** when wiping system files or drives
7. **Perform a dry run** first for critical operations

## Getting Help

### Command Help

Display the help menu:

```bash
python secure_eraser.py --help
```

### Method Information

Get information about a specific wiping method:

```bash
python secure_eraser.py --method-info dod_7pass
```

### Version Information

Display version and system information:

```bash
python secure_eraser.py --version
```

## Troubleshooting

If you encounter issues, try:

1. Running with `--verbose` for detailed information
2. Checking file and directory permissions
3. Using `--force` if appropriate for the operation
4. Running with administrative privileges for drive operations
5. Verifying Python version and dependencies
6. Consulting the troubleshooting guide for specific errors

## Related Documentation

- [Security Standards](security_standards.md) - Details on available wiping methods
- [Performance](performance.md) - Performance optimization options
- [Verification](verification.md) - In-depth verification information
- [Troubleshooting](troubleshooting.md) - Solutions for common issues