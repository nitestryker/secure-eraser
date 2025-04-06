# Verification

This guide explains Secure Eraser's verification features, which ensure that data has been properly and securely erased.

## Understanding Verification

Verification is a critical step in the secure erasure process. It confirms that data has been properly overwritten and is unrecoverable. Secure Eraser implements multiple verification methods:

1. **Pattern Verification**: Confirms overwrite patterns were correctly applied
2. **Hash Verification**: Cryptographically verifies that content has changed
3. **Sampling Verification**: Checks representative portions of large targets
4. **Multi-Algorithm Verification**: Uses multiple hash functions for added security

## Basic Verification

Enable basic verification with the `--verify` flag:

```bash
python secure_eraser.py --file /path/to/file.txt --verify
```

This performs standard verification after wiping:
- Checks that overwrite patterns were correctly applied
- Verifies file contents match expected patterns
- Uses SHA-256 as the default hash algorithm

## Verification Levels

Secure Eraser supports different verification levels:

### Standard Verification

```bash
python secure_eraser.py --file /path/to/file.txt --verify --verification-level standard
```

- Default level if not specified
- Balances thoroughness with performance
- Suitable for most operations

### Sample Verification

```bash
python secure_eraser.py --file /path/to/file.txt --verify --verification-level sample
```

- For very large files or drives
- Checks random samples across the target
- Faster but less comprehensive

### Full Verification

```bash
python secure_eraser.py --file /path/to/file.txt --verify --verification-level full
```

- Most thorough verification
- Checks entire target content
- Slower but most secure
- Recommended for highly sensitive data

## Hash Algorithms

Specify which cryptographic hash algorithms to use:

```bash
python secure_eraser.py --file /path/to/file.txt --verify --hash-algorithms sha256,md5,sha1
```

Supported algorithms:
- MD5 (less secure, but fast)
- SHA-1 (legacy, moderate security)
- SHA-256 (default, good security)
- SHA-512 (highest security, slower)
- BLAKE2 (modern, high performance)

For maximum security, use multiple algorithms:

```bash
python secure_eraser.py --file /path/to/file.txt --verify --hash-algorithms sha256,sha512,blake2b
```

## Before and After Hashing

Secure Eraser generates hashes before and after wiping:

1. **Before Hash**: Computed before any wiping is performed
2. **Wiping Process**: Multiple passes of data overwriting
3. **After Hash**: Computed after wiping is complete
4. **Comparison**: The hashes are compared to ensure they differ

The hash change confirms that the file content has been modified. If the hashes match, it indicates a verification failure.

## Verification Process Details

### For Files

```bash
python secure_eraser.py --file /path/to/file.txt --verify --verbose
```

The verification process for files includes:
1. Computing initial hash values of the file
2. Performing the requested wiping method
3. Computing final hash values after wiping
4. Comparing hashes to ensure they've changed
5. Checking that the file now contains the expected patterns
6. Generating verification results in the console and reports

### For Directories

```bash
python secure_eraser.py --dir /path/to/directory --verify
```

When verifying directory wiping:
1. Each file is individually verified
2. A summary verification report is generated
3. Both individual and aggregate results are reported

### For Drives

```bash
python secure_eraser.py --drive /path/to/drive --verify
```

For drive verification:
1. Key sectors are sampled (boot sector, partition table, etc.)
2. Random sectors throughout the drive are verified
3. Sector-level hash verification is performed
4. Results include sector-specific verification

## Advanced Verification Features

### Custom Verification Sampling

For large targets, customize the sampling rate:

```bash
python secure_eraser.py --drive /path/to/drive --verify --sampling-rate 0.15
```

This verifies 15% of the drive, randomly distributed.

### Verification-Only Mode

To verify a previously wiped target without rewlping:

```bash
python secure_eraser.py --file /path/to/wiped_file.txt --verify-only
```

This checks if the file appears to have been properly wiped, without performing any new wiping operations.

### Pattern-Specific Verification

For methods with specific patterns:

```bash
python secure_eraser.py --file /path/to/file.txt --method dod_7pass --verify --pattern-verification
```

This specifically checks for the expected patterns from the DOD 7-pass method.

## Verification Reporting

Get detailed verification information in reports:

```bash
python secure_eraser.py --file /path/to/file.txt --verify --report-format html --report-path verification_report.html
```

Verification reports include:
- Before and after hash values
- Verification methodology
- Pass/fail status for each verification method
- Visual representations of verification results
- Timestamp and system information

### Digital Signatures

Add digital signatures to verification reports:

```bash
python secure_eraser.py --file /path/to/file.txt --verify --sign-report
```

Digital signatures ensure the verification report hasn't been altered after generation.

## Interpreting Verification Results

Verification results are clearly indicated:

- **Success**: All verification checks passed
- **Partial Success**: Some verification methods passed, others failed
- **Failure**: All verification checks failed

Common verification failure causes:
1. **File System Caching**: May prevent proper reading of on-disk data
2. **Write Failures**: Some sectors might be bad or protected
3. **Hardware Issues**: Failing drives may not properly write data
4. **File System Features**: Copy-on-write or journaling can affect verification
5. **SSD Wear Leveling**: SSDs may redirect writes to different physical locations

## Verification for Special Media Types

### SSD Verification

For solid-state drives:

```bash
python secure_eraser.py --drive /path/to/ssd --verify --media-type ssd
```

This uses SSD-specific verification that accounts for wear leveling.

### RAID Verification

For RAID arrays:

```bash
python secure_eraser.py --drive /path/to/raid --verify --raid-aware
```

This applies verification across all disks in the array.

## Verification Best Practices

1. **Always use verification** for sensitive data
2. **Use full verification** for highly sensitive information
3. **Use multiple hash algorithms** for critical data
4. **Generate reports** for compliance and auditing
5. **Check verification logs** for any warnings or errors
6. **Consider filesystem specifics** when verifying
7. **Use stronger verification** for SSDs and virtual drives

## Troubleshooting Verification

### Verification Failures

If verification fails:

1. **Check permissions**: Ensure you have proper read access
2. **Disable caching**: Use system calls to flush caches before verification
3. **Try a different wiping method**: Some methods work better on specific media
4. **Check for file system features**: Compression, deduplication, etc.
5. **Check hardware health**: Run diagnostics on the storage device

### Performance Issues

If verification is too slow:

1. **Reduce verification level**: Use sampling for large drives
2. **Use faster hash algorithms**: MD5 is faster but less secure
3. **Adjust sampling rate**: Lower the percentage of data verified
4. **Disable multiple algorithms**: Use a single strong algorithm

## Related Documentation

- [Security Standards](security_standards.md) - Understanding security methods
- [Reporting](reporting.md) - Detailed information on verification reports
- [Troubleshooting](troubleshooting.md) - General troubleshooting guide