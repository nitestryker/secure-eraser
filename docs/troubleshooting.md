# Troubleshooting Guide

This guide helps you diagnose and resolve common issues that may occur when using Secure Eraser.

## General Troubleshooting Process

Follow these general steps when encountering problems:

1. **Check the command syntax** using `--help`
2. **Enable verbose mode** with `--verbose` or `--debug` for more detailed output
3. **Check system logs** for related errors
4. **Verify permissions** on target files and directories
5. **Check available disk space**
6. **Ensure dependencies** are correctly installed

## Common Issues and Solutions

### Installation Issues

#### Missing Dependencies

**Symptoms:**
- Error messages about missing modules
- ImportError exceptions

**Solutions:**
```bash
# Install required dependencies
pip install psutil py-cpuinfo reportlab jinja2 matplotlib

# For GPU support
pip install pycuda numpy
```

#### Invalid Python Version

**Symptoms:**
- SyntaxError or TypeError messages
- Features not working as expected

**Solution:**
Ensure you're using Python 3.9 or higher:
```bash
python --version
# If needed, upgrade Python or use a specific version
python3.9 secure_eraser.py [options]
```

### Permission Issues

#### Access Denied to Files

**Symptoms:**
- "Permission denied" errors
- Operations fail without detailed errors

**Solutions:**
```bash
# Check file permissions
ls -la /path/to/file.txt

# Change file permissions if needed
chmod 600 /path/to/file.txt

# Run with elevated privileges (with caution)
sudo python secure_eraser.py --file /path/to/file.txt
```

#### Access Denied to Drives

**Symptoms:**
- Drive operations fail with permission errors
- System files cannot be accessed

**Solutions:**
```bash
# Run with elevated privileges for drive operations
sudo python secure_eraser.py --drive /path/to/drive --force

# Check mount options
mount | grep /path/to/drive
```

### Performance Issues

#### Slow Operation

**Symptoms:**
- Operations take longer than expected
- High resource usage but low throughput

**Solutions:**
```bash
# Enable GPU acceleration if available
python secure_eraser.py --file /path/to/file.txt --gpu

# Adjust worker count
python secure_eraser.py --file /path/to/file.txt --workers 4

# Use a simpler wiping method
python secure_eraser.py --file /path/to/file.txt --method standard --passes 3
```

#### High Resource Usage

**Symptoms:**
- System becomes unresponsive
- Other applications are affected

**Solutions:**
```bash
# Enable resource optimization
python secure_eraser.py --file /path/to/file.txt --optimize-resources

# Reduce worker count
python secure_eraser.py --file /path/to/file.txt --workers 2

# Use smaller chunks
python secure_eraser.py --file /path/to/file.txt --chunk-size 10
```

### Verification Issues

#### Verification Fails

**Symptoms:**
- "Verification failed" messages
- Hash values remain unchanged

**Solutions:**
```bash
# Check if file is actually writable
# Some files may appear writable but have special restrictions
touch /path/to/file.txt

# Try a different wiping method
python secure_eraser.py --file /path/to/file.txt --method dod --verify

# Check disk health
smartctl -a /dev/sda  # Replace with your drive
```

#### Hash Algorithm Errors

**Symptoms:**
- "Unknown hash algorithm" errors
- Hash computation fails

**Solutions:**
```bash
# Use a different hash algorithm
python secure_eraser.py --file /path/to/file.txt --verify --hash-algorithms sha256

# Ensure hashlib is properly installed
python -c "import hashlib; print(hashlib.algorithms_available)"
```

### Reporting Issues

#### Report Generation Fails

**Symptoms:**
- "Failed to generate report" errors
- Empty or corrupted report files

**Solutions:**
```bash
# Check dependencies
python -c "import reportlab, jinja2, matplotlib"

# Try a different report format
python secure_eraser.py --file /path/to/file.txt --verify --report-format json

# Ensure write permissions for report destination
touch /path/to/reports/test.txt && rm /path/to/reports/test.txt
```

#### Visualization Issues

**Symptoms:**
- Missing charts in HTML reports
- "Failed to generate chart" errors

**Solutions:**
```bash
# Update matplotlib
pip install --upgrade matplotlib

# Try a simpler report format
python secure_eraser.py --file /path/to/file.txt --verify --report-format json
```

### GPU Acceleration Issues

#### GPU Not Detected

**Symptoms:**
- "No CUDA-capable device detected" errors
- GPU flag is ignored

**Solutions:**
```bash
# Check CUDA installation
nvidia-smi

# Verify PyCUDA installation
python -c "import pycuda.autoinit; print('CUDA OK')"

# Fall back to CPU mode
python secure_eraser.py --file /path/to/file.txt  # Without --gpu flag
```

#### GPU Out of Memory

**Symptoms:**
- "Out of memory" or "Insufficient memory" errors
- GPU operations fail for large files

**Solutions:**
```bash
# Reduce chunk size
python secure_eraser.py --file /path/to/file.txt --gpu --chunk-size 10

# Use CPU for very large files
python secure_eraser.py --file /path/to/file.txt  # Without --gpu flag
```

### Job Management Issues

#### Can't Resume Job

**Symptoms:**
- "Job not found" errors
- Resume operation fails

**Solutions:**
```bash
# List available jobs
python secure_eraser.py --list-jobs

# Check job database integrity
python secure_eraser.py --check-job-database

# If database is corrupted, repair it
python secure_eraser.py --repair-job-database
```

#### Job Gets Stuck

**Symptoms:**
- Operation progress stops
- No error messages, but no progress

**Solutions:**
```bash
# Try canceling and restarting the job
python secure_eraser.py --cancel-job job_id
python secure_eraser.py --file /path/to/file.txt

# Check system resources
top
df -h
```

### Custom Pattern Issues

#### Pattern Creation Fails

**Symptoms:**
- "Invalid pattern" errors
- Pattern not saved

**Solutions:**
```bash
# Ensure hex pattern is valid
python secure_eraser.py --create-pattern test_pattern --pattern-hex "AABBCCDD"

# Check pattern length (must be even)
python secure_eraser.py --create-pattern test_pattern --pattern-hex "AABBCC"  # Wrong
python secure_eraser.py --create-pattern test_pattern --pattern-hex "AABBCCDD"  # Correct
```

#### Pattern Not Found

**Symptoms:**
- "Pattern not found" errors
- Custom pattern not applied

**Solutions:**
```bash
# List available patterns
python secure_eraser.py --list-patterns

# Check pattern name spelling
python secure_eraser.py --custom-pattern my_pattern  # Case sensitive
```

### Web Interface Issues

#### Interface Won't Start

**Symptoms:**
- "Address already in use" errors
- Web server fails to start

**Solutions:**
```bash
# Check if port 5000 is already in use
netstat -tuln | grep 5000

# Use a different port
python main.py --port 8080
```

#### Demo Operation Fails

**Symptoms:**
- Error messages in demo output
- Demo doesn't complete

**Solutions:**
```bash
# Check Secure Eraser functionality directly
python secure_eraser.py --file /tmp/test.txt

# Check Flask installation
python -c "import flask; print(flask.__version__)"
```

## Advanced Troubleshooting

### Diagnostic Mode

For difficult issues, use diagnostic mode:

```bash
python secure_eraser.py --diagnostic
```

This runs a series of tests to verify system compatibility and tool functionality.

### Log Collection

Collect comprehensive logs for analysis:

```bash
python secure_eraser.py --file /path/to/file.txt --debug --log-file detailed.log
```

### Environment Information

Gather system and environment information:

```bash
python secure_eraser.py --system-info
```

This displays detailed information about your system that can help with troubleshooting.

## Getting Help

If you cannot resolve an issue using this guide:

1. **Check Documentation**: Review relevant sections of the documentation
2. **Search Issues**: Check for known issues in the project repository
3. **Community Support**: Ask for help in the user forums or community channels
4. **Contact Support**: Submit a detailed support request with logs and environment information
5. **Submit a Bug Report**: If you've found a bug, submit a detailed report with reproduction steps

## Common Error Messages

Here's a quick reference for common error messages and their likely causes:

| Error Message | Likely Cause | Solution |
|---------------|--------------|----------|
| "Permission denied" | Insufficient file permissions | Check permissions, use sudo if appropriate |
| "No such file or directory" | Target file doesn't exist or path is wrong | Verify file path |
| "Failed to verify wiping" | File could not be properly wiped | Check file system, storage health |
| "Device or resource busy" | File is locked by another process | Close other applications using the file |
| "Not enough free space" | Insufficient disk space | Free up disk space |
| "Invalid wiping method" | Method name is incorrect | Check spelling and available methods |
| "Hash algorithm not supported" | Invalid hash algorithm specified | Use a supported algorithm |
| "Failed to initialize GPU" | GPU issues | Check CUDA installation, fall back to CPU |
| "Job database error" | Corrupted job database | Repair or reset job database |
| "Verification hash mismatch" | File wasn't properly wiped | Try different method or check storage device |

## Related Documentation

- [Installation](installation.md) - Resolving dependency and installation issues
- [Performance](performance.md) - Optimizing performance
- [Job Management](job_management.md) - Managing and troubleshooting jobs
- [Web Interface](web_interface.md) - Web interface troubleshooting