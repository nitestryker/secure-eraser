# Filename and Metadata Wiping

This guide explains how to use Secure Eraser's filename and metadata wiping features to ensure complete removal of all traces of sensitive files, not just their contents.

## Understanding Metadata Security Risks

When securely erasing files, it's important to recognize that sensitive information can persist in:

1. **Filenames**: The original name might reveal confidential information
2. **File Metadata**: Creation dates, modification history, author information, etc.
3. **File System Records**: Directory entries, MFT (Master File Table) records, etc.
4. **File System Journal**: Records of file operations that can reveal previous existence

Even when file contents are securely wiped, these metadata elements can leak information about what was deleted.

## Basic Metadata Wiping

Enable basic metadata wiping with the `--wipe-metadata` flag:

```bash
python secure_eraser.py --file /path/to/sensitive_file.txt --wipe-metadata
```

This performs:
- Filename randomization before deletion
- Timestamp manipulation
- Basic attribute clearing

## Complete File Shredding

For maximum security, use the complete shredding option:

```bash
python secure_eraser.py --file /path/to/sensitive_file.txt --shred
```

The `--shred` option combines:
- File content wiping using the specified method
- Full metadata wiping
- Multiple file renames with random names
- File size manipulation
- Directory entry overwriting

## Advanced Metadata Controls

### Filename Randomization

Control how filenames are randomized before deletion:

```bash
python secure_eraser.py --file /path/to/sensitive_file.txt --rename-iterations 5
```

This renames the file 5 times with random names before wiping and deletion.

### Timestamp Manipulation

Control timestamp manipulation:

```bash
python secure_eraser.py --file /path/to/sensitive_file.txt --wipe-timestamps
```

This option specifically targets the creation, modification, and access timestamps.

### Extended Attribute Cleaning

Wipe extended attributes and alternate data streams:

```bash
python secure_eraser.py --file /path/to/sensitive_file.txt --wipe-xattr
```

This targets system-specific extended file attributes.

## File System-Specific Metadata Wiping

Different file systems store metadata differently. Secure Eraser can target specific file system structures:

### NTFS-Specific Options

For Windows NTFS file systems:

```bash
python secure_eraser.py --file /path/to/sensitive_file.txt --ntfs-cleanup
```

This option includes:
- MFT record cleaning
- USN journal record removal
- Alternate data stream removal

### ext4-Specific Options

For Linux ext4 file systems:

```bash
python secure_eraser.py --file /path/to/sensitive_file.txt --ext4-cleanup
```

This option includes:
- Inode wiping
- Journal record cleaning

### HFS+/APFS-Specific Options

For macOS file systems:

```bash
python secure_eraser.py --file /path/to/sensitive_file.txt --apfs-cleanup
```

This option includes:
- Catalog record cleaning
- Attribute cleanup

## Directory Metadata Wiping

When wiping directories, metadata cleanup is even more important:

```bash
python secure_eraser.py --dir /path/to/sensitive_directory --recursive --wipe-metadata
```

This recursively processes all files and also handles:
- Directory entry wiping
- Directory attribute cleaning
- Internal structure reorganization before deletion

## Scheduled Metadata Wiping

Set up regular metadata cleaning for temporary/cache directories:

```bash
python secure_eraser.py --schedule-metadata-cleaning --targets "/tmp,/cache" --interval daily
```

This performs metadata-only cleaning on a schedule without necessarily wiping the file contents.

## Combining with Content Wiping

For maximum security, combine metadata wiping with strong content wiping methods:

```bash
python secure_eraser.py --file /path/to/top_secret.docx --method dod_7pass --shred --verification-level full
```

This provides:
- 7-pass DoD standard content wiping
- Complete metadata removal
- Full verification of both content and metadata wiping

## Metadata Wiping Reports

Generate reports that include metadata wiping details:

```bash
python secure_eraser.py --file /path/to/file.txt --shred --report-format html --report-path shred_report.html
```

These reports include:
- Details of metadata elements wiped
- Verification of directory entry removal
- Before/after filesystem record status

## Verification of Metadata Wiping

Verify that metadata has been properly wiped:

```bash
python secure_eraser.py --file /path/to/wiped_file.txt --verify-metadata
```

This performs:
- Checks for residual filename references
- File system journal scanning
- MFT/inode record verification

## Special Cases

### Wiping Within Archive Files

Clean metadata within archives without extracting:

```bash
python secure_eraser.py --archive /path/to/archive.zip --clean-metadata
```

This cleans metadata from files inside ZIP, TAR, and other archive formats.

### Document Metadata Cleaning

Target embedded metadata in document files:

```bash
python secure_eraser.py --file /path/to/document.docx --document-metadata
```

This specifically targets document properties like author, company, revision history, etc.

### Email Metadata Cleaning

When wiping email files, target mail-specific metadata:

```bash
python secure_eraser.py --file /path/to/emails.pst --email-metadata
```

This cleans headers, routing information, and other email-specific metadata.

## Best Practices

1. **Always use metadata wiping** for sensitive files
2. **Use the `--shred` option** for the most sensitive data
3. **Perform verification** to confirm complete removal
4. **Consider file system specifics** when setting options
5. **Use multiple rename iterations** for critical data
6. **Combine with secure content wiping** for complete security
7. **Generate detailed reports** for compliance and auditing

## Technical Notes

### System Requirements

Metadata wiping requires specific permissions:
- Administrative access for some filesystem operations
- Full control permissions on the target files
- Appropriate system calls for different operating systems

### File System Compatibility

Metadata wiping effectiveness varies by file system:
- Most effective: NTFS, ext4, HFS+, APFS
- Partially effective: FAT32, exFAT
- Limited effectiveness: Network file systems (care should be taken)

## Related Documentation

- [Basic Usage](basic_usage.md) - Fundamental file wiping operations
- [Security Standards](security_standards.md) - Content wiping security standards
- [Verification](verification.md) - Verifying wiping effectiveness