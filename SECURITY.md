# Security Features of SecureEraser

## Overview
SecureEraser is designed to provide robust security features for permanent file erasure. This document outlines the security features implemented in the SecureEraser tool, including military-grade wiping standards, anti-forensic techniques, cryptographic verification, and secure memory handling.

## Military-Grade Wiping Standards

SecureEraser implements the following military and government security standards for data wiping:

### NIST SP 800-88 Standards
* **NIST Clear (nist_clear)**: Single-pass zero overwrite for non-sensitive data
* **NIST Purge (nist_purge)**: Single-pass one overwrite for sensitive data

### Department of Defense Standards
* **DoD 5220.22-M (3-pass) (dod_3pass)**: Standard DoD method using 3 passes
  - Pass 1: All zeros (0x00)
  - Pass 2: All ones (0xFF)
  - Pass 3: Random data
* **DoD 5220.22-M (7-pass) (dod_7pass)**: Extended DoD method using 7 passes
  - Pass 1: All zeros (0x00)
  - Pass 2: All ones (0xFF)
  - Pass 3: Random data
  - Pass 4: Random data
  - Pass 5: All zeros (0x00)
  - Pass 6: All ones (0xFF)
  - Pass 7: Random data

### UK Government Standards
* **HMG IS5 Baseline (hmg_is5_baseline)**: UK Government baseline method using 1 pass of random data
* **HMG IS5 Enhanced (hmg_is5_enhanced)**: UK Government enhanced method using 3 passes
  - Pass 1: All zeros (0x00)
  - Pass 2: Random data
  - Pass 3: Verification pass

### US Military Branch Standards
* **NAVSO P-5239-26 (navso)**: US Navy standard using 3 passes
  - Pass 1: Character (0x01)
  - Pass 2: Complement (0xFE)
  - Pass 3: Random data
* **AFSSI-5020 (afssi)**: Air Force standard (equivalent to DoD 3-pass)
* **AR 380-19 (ar_380_19)**: Army standard using 7 passes
  - Pass 1: Random data
  - Pass 2: Specified character (0xFE)
  - Pass 3: Complement (0x01)
  - Pass 4-7: Random data

### NSA Standard
* **CSC-STD-005-85 (csc)**: NSA standard for sanitizing classified information using 7 passes
  - Pass 1: All zeros (0x00)
  - Pass 2: All ones (0xFF)
  - Pass 3: Random data
  - Pass 4: Pattern A (0x96)
  - Pass 5: Complement of Pattern A (0x69)
  - Pass 6: Pattern B (0xAA)
  - Pass 7: Complement of Pattern B (0x55)

## Custom Wiping Patterns

SecureEraser allows users to create, manage, and use custom wiping patterns:

* **Byte Patterns**: Create custom byte patterns from hex strings (e.g., "DEADBEEF")
* **Multi-Pass Patterns**: Define complex multi-pass wiping strategies
* **Pattern Generators**: Use built-in pattern generators for specialized requirements:
  - Random: Cryptographically secure random data
  - Zeros/Ones: All zeros (0x00) or all ones (0xFF)
  - Alternating Patterns: Alternating bits (0x55, 0xAA) or bytes (0x00, 0xFF)
  - Random Complement: Random data followed by its complement
  - ASCII Noise: Random printable ASCII characters
  - Fibonacci: Fibonacci sequence as byte pattern
  - Counter: Incrementing counter pattern
  - Random Blocks: Random block sizes with random data

## Cryptographic Verification

* **Pre-Wiping Hash Computation**: Calculates cryptographic hashes before wiping
* **Post-Wiping Hash Verification**: Ensures data cannot be recovered by comparing pre and post-wiping hashes
* **Multiple Hash Algorithms**: Supports SHA-256, SHA3-256, SHA3-512, and SHA-512
* **Digital Signing**: Verification reports can be digitally signed using HMAC

## Secure Memory Handling

* **Secure Memory Allocation**: Implements secure memory allocation techniques
* **Memory Locking**: Prevents sensitive data from being swapped to disk
* **Memory Zeroing**: Securely zeroes memory after use
* **Memory Protection**: Prevents unauthorized access to sensitive memory regions

## Anti-Forensic Techniques

* **File Attribute Scrubbing**: Removes file metadata before deletion
* **Timestamp Manipulation**: Randomizes file timestamps to prevent forensic timeline analysis
* **Path Obfuscation**: Uses random temporary paths during secure deletion
* **Parallel Operations**: Performs multiple wiping operations simultaneously to increase effectiveness
* **Secure Random Number Generation**: Uses cryptographically secure random number generators

## Verification and Reporting

* **Comprehensive Verification**: Validates wiping success with multiple methods
* **Detailed Reports**: Generates detailed wiping reports in multiple formats (JSON, PDF, HTML)
* **Visualizations**: HTML reports include charts and visualizations of the wiping process
* **Digital Signatures**: Reports can be digitally signed for authenticity verification

## Performance Security Features

* **GPU Acceleration**: Uses GPU for faster random data generation and pattern creation
* **Resource-Aware Operations**: Adjusts resource usage based on system load
* **Secure Job Control**: Allows secure pausing and resuming of wiping jobs
* **Batch Processing**: Securely processes multiple files with consistent security policies

## Secure Implementation Details

* **Filesystem Syncing**: Forces filesystem syncs to ensure overwrites are committed to physical media
* **Block-Level Operations**: Uses low-level block operations where possible
* **Secure Error Handling**: Handles errors securely without leaking sensitive information
* **Audit Logging**: Maintains detailed secure logs of all operations

## Compliance and Best Practices

SecureEraser is designed with common security standards and best practices in mind, including:

* NIST SP 800-88 Guidelines for Media Sanitization
* DoD 5220.22-M National Industrial Security Program Operating Manual
* Common Criteria security guidelines
* OWASP secure coding practices

## Security Limitations

The effectiveness of secure deletion depends on several factors:

* **Storage Technology**: SSDs, flash-based storage, and modern file systems (like NTFS or ext4) may retain data due to wear-leveling, journaling, or other features
* **File System Behavior**: Some file systems may preserve file data in journal or other metadata areas
* **Physical Access**: These methods do not protect against sophisticated physical recovery techniques
* **Hidden Storage Areas**: Modern drives may have hidden areas not accessible through normal interfaces

## Contact

If you discover any security-related issues, please email security@example.com instead of using the issue tracker.