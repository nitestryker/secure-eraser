# Custom Wiping Patterns

This guide explains how to use Secure Eraser's custom pattern functionality to create and apply specialized data wiping patterns for your specific security requirements.

## Understanding Custom Patterns

Custom wiping patterns allow you to define exactly what data is written over your files during the secure erasure process. This is useful for:

1. **Specialized Security Requirements**: Organizations with specific overwrite standards
2. **Compliance with Specific Regulations**: Meeting particular regulatory requirements
3. **Customized Security Levels**: Balancing performance and security
4. **Testing and Verification**: Confirming wiping effectiveness with known patterns

## Creating Custom Patterns

### Basic Pattern Creation

To create a simple custom pattern:

```bash
python secure_eraser.py --create-pattern test_pattern --pattern-hex "DEADBEEF"
```

This creates a pattern named "test_pattern" that will write the hexadecimal values 0xDE, 0xAD, 0xBE, 0xEF repeatedly when used.

### Complex Pattern Creation

For more complex patterns:

```bash
python secure_eraser.py --create-pattern financial_data --pattern-hex "00112233445566778899AABBCCDDEEFF"
```

Patterns can be any length (though they must contain an even number of characters to form complete bytes).

### Creating Random Patterns

Generate a cryptographically secure random pattern:

```bash
python secure_eraser.py --create-pattern random_pattern --random-pattern --pattern-length 16
```

This creates a random 16-byte pattern named "random_pattern".

## Using Custom Patterns

To use a custom pattern for wiping:

```bash
python secure_eraser.py --file /path/to/file.txt --custom-pattern test_pattern
```

This applies the "test_pattern" to wipe the file.

### Specifying Multiple Passes

For multiple passes with a custom pattern:

```bash
python secure_eraser.py --file /path/to/file.txt --custom-pattern test_pattern --passes 7
```

This applies the pattern 7 times for extra security.

### Alternating with Other Methods

You can create a multi-step wiping process with different methods:

```bash
python secure_eraser.py --file /path/to/file.txt --multi-method "custom:test_pattern,random,zero"
```

This applies the custom pattern, followed by a random data pass, followed by a zero pass.

## Managing Custom Patterns

### Listing Available Patterns

To view all available custom patterns:

```bash
python secure_eraser.py --list-patterns
```

This displays all stored custom patterns with details:
- Pattern name
- Hexadecimal representation
- Creation date
- Pattern length

### Deleting Patterns

To remove a custom pattern:

```bash
python secure_eraser.py --delete-pattern test_pattern
```

This permanently removes the pattern named "test_pattern".

### Exporting Patterns

Export patterns for backup or sharing:

```bash
python secure_eraser.py --export-patterns /path/to/patterns.json
```

This saves all custom patterns to the specified file.

### Importing Patterns

Import patterns from a file:

```bash
python secure_eraser.py --import-patterns /path/to/patterns.json
```

This loads custom patterns from the specified file.

## Advanced Pattern Features

### Inverting Patterns

Create and use an inverted pattern (bitwise NOT):

```bash
python secure_eraser.py --file /path/to/file.txt --custom-pattern test_pattern --invert-pattern
```

This applies the bitwise inverse of the specified pattern.

### Pattern Reporting

Generate detailed reports about pattern application:

```bash
python secure_eraser.py --file /path/to/file.txt --custom-pattern test_pattern --verify --report-format html --report-path pattern_report.html
```

The report includes:
- Pattern representation
- Application details
- Verification results

### Pattern Visualization

For a visual representation of a pattern:

```bash
python secure_eraser.py --visualize-pattern test_pattern
```

This displays a graphical representation of the pattern.

## Custom Pattern Best Practices

1. **Use Cryptographically Strong Patterns**: Random or complex patterns for sensitive data
2. **Document Pattern Purposes**: Keep records of which patterns are used for what purpose
3. **Regular Auditing**: Periodically review and clean up unused patterns
4. **Pattern Length**: Longer patterns provide more variability
5. **Multiple Passes**: Use multiple passes for stronger security
6. **Testing**: Verify pattern effectiveness before using in production

## Pattern Security Considerations

### Pattern Strength

Pattern security depends on several factors:
- **Length**: Longer patterns are generally more secure
- **Randomness**: More random patterns are harder to predict
- **Complexity**: Patterns with varied byte values are stronger
- **Purpose**: Some patterns are designed for specific media types

### Pattern Storage Security

Custom patterns are stored in a secure location with the following protections:
- **Encrypted Storage**: Patterns are stored in an encrypted format
- **Access Control**: Only users with appropriate permissions can access patterns
- **Integrity Checking**: Storage includes checksums to detect tampering

## Specialized Pattern Use Cases

### SSD Optimized Patterns

For solid-state drives:

```bash
python secure_eraser.py --create-pattern ssd_optimized --pattern-hex "FFFFFFFF00000000AAAAAAAA55555555"
```

This pattern is designed to work well with SSD wear-leveling algorithms.

### RAID Optimized Patterns

For RAID arrays:

```bash
python secure_eraser.py --create-pattern raid_pattern --pattern-hex "DEADBEEFDEADBEEFDEADBEEFDEADBEEF"
```

Patterns with high repetition can be more effective for some RAID configurations.

### Compliance Patterns

For regulatory compliance:

```bash
python secure_eraser.py --create-pattern pci_dss --pattern-hex "00000000FFFFFFFF55555555AAAAAAAA"
```

Create patterns that meet specific regulatory requirements.

## Troubleshooting Custom Patterns

### Pattern Not Found

If a pattern cannot be found:
- Check the pattern name for typos
- Ensure the pattern was created successfully
- Verify you're running as the same user who created the pattern
- Check if the pattern storage is accessible

### Invalid Pattern Error

If you get "Invalid pattern" errors:
- Ensure hexadecimal values are valid (0-9, A-F)
- Check that the pattern has an even number of characters
- Verify the length is not exceeding system limits

### Pattern Verification Failures

If pattern verification fails:
- Check file permissions
- Ensure the file is not locked by another process
- Try a different verification method
- Check if the storage media is functioning properly

## Related Documentation

- [Security Standards](security_standards.md) - Standard wiping methods
- [Verification](verification.md) - Verifying wiping effectiveness
- [Performance](performance.md) - Performance considerations for different patterns