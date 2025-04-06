# Security Standards

This guide explains the security standards implemented in Secure Eraser, including military-grade data destruction methods, compliance standards, and custom security options.

## Core Security Principles

Secure Eraser is built on three core security principles:

1. **True Data Destruction**: Ensuring data cannot be recovered even with advanced forensic tools
2. **Verification**: Cryptographic confirmation of successful erasure
3. **Auditability**: Comprehensive logging and reporting for compliance

## Supported Security Standards

### NIST 800-88 Standards

The National Institute of Standards and Technology (NIST) Special Publication 800-88 defines guidelines for media sanitization:

#### NIST Clear

```bash
python secure_eraser.py --file /path/to/file.txt --method nist_clear
```

- Single overwrite with fixed patterns
- Suitable for moderately sensitive data
- Protects against standard recovery tools

#### NIST Purge

```bash
python secure_eraser.py --file /path/to/file.txt --method nist_purge
```

- Multiple overwrites with varying patterns
- Suitable for sensitive data
- Protects against advanced recovery tools
- Default method for important data

### DoD Standards

The Department of Defense standards for data wiping:

#### DoD 5220.22-M (3-pass)

```bash
python secure_eraser.py --file /path/to/file.txt --method dod_3pass
```

- Pass 1: Fixed character (0xFF)
- Pass 2: Complement of first pass (0x00)
- Pass 3: Random characters
- Verification pass

#### DoD 5220.22-M ECE (7-pass)

```bash
python secure_eraser.py --file /path/to/file.txt --method dod_7pass
```

- Extended 7-pass variant
- Alternating pattern and random character writes
- Final random character pass
- Verification pass
- Higher security than 3-pass variant

### British HMG IS5 Standards

British Government security standards:

#### HMG IS5 Enhanced

```bash
python secure_eraser.py --file /path/to/file.txt --method hmg_enhanced
```

- Three passes with verification
- Specialized for government data
- Compliant with UK security requirements

#### HMG IS5 Higher

```bash
python secure_eraser.py --file /path/to/file.txt --method hmg_higher
```

- Enhanced version with additional passes
- Suitable for highly classified information
- Includes random verification

### Peter Gutmann Standard

A comprehensive 35-pass overwrite method:

```bash
python secure_eraser.py --file /path/to/file.txt --method gutmann
```

- 35 passes using different patterns
- Designed to defeat all known recovery methods
- Historical standard for maximum security
- Time-consuming but extremely thorough

### Bruce Schneier Algorithm

Seven-pass overwrite method developed by cryptography expert Bruce Schneier:

```bash
python secure_eraser.py --file /path/to/file.txt --method schneier
```

- Pass 1: All ones (0xFF)
- Pass 2: All zeros (0x00)
- Passes 3-7: Random data
- Good balance of security and performance

### Random Data Methods

Simple overwriting with random data:

#### Single Pass Random

```bash
python secure_eraser.py --file /path/to/file.txt --method random --passes 1
```

- Fast method for less sensitive data
- Minimal security against basic recovery

#### Multi-Pass Random

```bash
python secure_eraser.py --file /path/to/file.txt --method random --passes 10
```

- Configurable number of passes
- Increased security with more passes
- Good for custom security requirements

### Zero-Fill Method

Simple overwriting with zeros:

```bash
python secure_eraser.py --file /path/to/file.txt --method zero --passes 1
```

- Fastest method
- Minimal security
- Useful for quick clearing of non-sensitive data

## Custom Security Patterns

Create and use custom wiping patterns for specialized requirements:

### Creating Custom Patterns

```bash
python secure_eraser.py --create-pattern finances --pattern-hex "DEADBEEF0123456789ABCDEF"
```

This creates a custom pattern named "finances" with the specified hex pattern.

### Using Custom Patterns

```bash
python secure_eraser.py --file /path/to/file.txt --custom-pattern finances --passes 7
```

This applies the custom "finances" pattern with 7 passes.

### Listing Available Patterns

```bash
python secure_eraser.py --list-patterns
```

This displays all available custom patterns.

### Deleting Custom Patterns

```bash
python secure_eraser.py --delete-pattern finances
```

This removes the "finances" pattern from the available patterns.

## Verification Methods

Secure Eraser supports multiple verification methods to confirm data destruction:

### Simple Verification

```bash
python secure_eraser.py --file /path/to/file.txt --verify
```

- Default verification
- Checks sample sectors for pattern compliance
- Efficient for most operations

### Comprehensive Verification

```bash
python secure_eraser.py --file /path/to/file.txt --verify --verification-level full
```

- Thorough verification of entire target
- Multiple hash algorithms used
- More time-consuming but most secure

### Cryptographic Verification

```bash
python secure_eraser.py --file /path/to/file.txt --verify --hash-algorithms sha256,sha512
```

- Uses specified hash algorithms
- Creates verification hashes
- Supports multiple algorithms simultaneously

## Compliance and Certification

For operations requiring regulatory compliance:

```bash
python secure_eraser.py --file /path/to/file.txt --method nist_purge --compliance-mode
```

Compliance mode:
- Generates detailed logs for auditing
- Creates compliance-ready reports
- Includes all required metadata for certification
- Maintains chain of custody information

### Supported Compliance Standards

Secure Eraser supports operations compliant with:

- NIST 800-88 Guidelines for Media Sanitization
- HIPAA Security Rule requirements
- PCI DSS data destruction requirements
- GDPR Article 17 (Right to Erasure) requirements
- ISO/IEC 27001 Information Security controls
- Various industry-specific regulations

## Security Best Practices

1. **Select the appropriate method** based on data sensitivity
2. **Always verify** wiping operations
3. **Use stronger methods** for more sensitive data
4. **Generate reports** for compliance and auditing
5. **Consider full-device encryption** before wiping for added security
6. **Use multiple passes** for magnetic media
7. **Remember that SSDs require special handling** due to wear leveling
8. **Use metadata wiping** for highly sensitive files to remove all traces
9. **Apply full file shredding** with the `--shred` option for maximum security

## Security Method Selection Guide

| Data Sensitivity | Recommended Method | Verification | Metadata Wiping |
|------------------|-------------------|-------------|-----------------|
| Public Data | zero or random (1-pass) | Sample | Not required |
| Internal Use | nist_clear or dod_3pass | Standard | Basic (--wipe-metadata) |
| Confidential | nist_purge or dod_7pass | Full | Basic (--wipe-metadata) |
| Highly Sensitive | hmg_higher or schneier | Full + Multiple Hashes | Advanced (--wipe-metadata --rename-iterations 5) |
| Classified | gutmann or shred | Full + Multiple Hashes | Complete (--shred) |

## Security Method Comparison

| Method | Passes | Performance | Security Level | Use Case |
|--------|--------|-------------|---------------|----------|
| zero | 1 | Very Fast | Minimal | Non-sensitive data |
| random | 1-100 | Varies | Basic to High | Configurable security |
| nist_clear | 1 | Fast | Basic | Routine sanitization |
| nist_purge | Multiple | Moderate | High | Sensitive data |
| dod_3pass | 3 | Moderate | Good | Military standard |
| dod_7pass | 7 | Slow | Very High | Classified data |
| hmg_enhanced | 3 | Moderate | Good | UK government |
| hmg_higher | Multiple | Slow | Very High | UK classified |
| gutmann | 35 | Very Slow | Maximum | Highest security |
| schneier | 7 | Slow | Very High | Cryptographic security |
| custom | Variable | Varies | Customizable | Specialized requirements |
| shred | Variable | Slow | Maximum+ | Complete elimination including metadata |

## Related Documentation

- [Basic Usage](basic_usage.md) - Command-line usage information
- [Verification](verification.md) - Detailed verification process
- [Custom Patterns](custom_patterns.md) - Creating and using custom wiping patterns
- [Metadata Wiping](metadata_wiping.md) - Removing filenames and metadata traces
- [Reporting](reporting.md) - Compliance and security reporting