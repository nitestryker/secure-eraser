# Secure Eraser Command Reference Guide

This document provides a comprehensive reference for all commands available in the `secure_eraser.py` tool, designed for secure data deletion and preparing computers for resale.

## Basic Command Structure

```
python secure_eraser.py [command] [arguments] [options]
```

## Available Commands

### 1. Wipe Free Space

Used to overwrite all free space on a drive, making previously deleted files unrecoverable.

```bash
python secure_eraser.py freespace [drive_path] [options]
```

**Arguments:**
- `drive_path`: Path to the drive/partition (e.g., `C:\` on Windows, `/home` on Linux)

**Options:**
- `--method [method]`: Wiping method to use (standard, dod, gutmann, paranoid)
- `--passes [number]`: Number of overwrite passes
- `--advanced`: Use OS-specific advanced wiping methods when available

**Examples:**
```bash
# Basic free space wiping with default method (3 passes)
python secure_eraser.py freespace C:\

# Department of Defense (DoD) standard wiping (7 passes)
python secure_eraser.py freespace C:\ --method dod

# Ultra-secure Gutmann method (35 passes) - very time-consuming
python secure_eraser.py freespace D:\ --method gutmann

# Standard method with custom number of passes
python secure_eraser.py freespace E:\ --passes 5

# Use advanced OS-specific tools when available
python secure_eraser.py freespace C:\ --advanced --method dod
```

### 2. Securely Delete a File

Securely overwrite and delete a specific file.

```bash
python secure_eraser.py file [file_path] [options]
```

**Arguments:**
- `file_path`: Path to the file to be securely deleted

**Options:**
- `--method [method]`: Wiping method to use (standard, dod, gutmann, paranoid)
- `--passes [number]`: Number of overwrite passes

**Examples:**
```bash
# Securely delete a file with default method (3 passes)
python secure_eraser.py file C:\Users\username\Documents\sensitive_file.pdf

# Delete using DoD standard
python secure_eraser.py file financial_data.xlsx --method dod

# Delete with custom number of passes
python secure_eraser.py file tax_records.pdf --passes 7
```

### 3. Securely Delete a Directory

Recursively overwrite and delete all files in a directory.

```bash
python secure_eraser.py directory [directory_path] [options]
```

**Arguments:**
- `directory_path`: Path to the directory to be securely deleted

**Options:**
- `--method [method]`: Wiping method to use (standard, dod, gutmann, paranoid)
- `--passes [number]`: Number of overwrite passes

**Examples:**
```bash
# Securely delete a directory with default method
python secure_eraser.py directory C:\Users\username\Documents\tax_records

# Delete using Gutmann method
python secure_eraser.py directory financial_data --method gutmann

# Delete with custom number of passes
python secure_eraser.py directory old_projects --passes 7
```

### 4. Full Drive Wipe (Computer Resale Preparation)

WARNING: This command provides guidance for completely wiping a drive for computer resale. It requires explicit confirmation.

```bash
python secure_eraser.py fullwipe [drive] [options]
```

**Arguments:**
- `drive`: Drive to wipe (e.g., `C:`, `/dev/sda`)

**Options:**
- `--method [method]`: Wiping method to use (standard, dod, gutmann, paranoid)
- `--passes [number]`: Number of overwrite passes
- `--force`: Skip confirmation prompt (USE WITH CAUTION)

**Examples:**
```bash
# Guidance for full drive wipe with DoD method
python secure_eraser.py fullwipe C: --method dod

# Guidance for full drive wipe with custom passes
python secure_eraser.py fullwipe /dev/sda --passes 9
```

## Wiping Methods

The tool supports four different wiping methods:

1. **standard**: Basic secure deletion with at least 3 passes
   - Pass 1: All zeros
   - Pass 2: All ones
   - Pass 3+: Random data

2. **dod**: Department of Defense 5220.22-M standard (7 passes)
   - Uses specific DoD-approved data patterns
   - Considered sufficient for most classified information

3. **gutmann**: Peter Gutmann's 35-pass method
   - Extremely thorough wiping method
   - Designed to counter even sophisticated laboratory recovery techniques
   - Very time-consuming

4. **paranoid**: Enhanced hybrid method (49+ passes)
   - Combines DoD and Gutmann methods
   - Maximum security for highly sensitive data

## Best Practices for Computer Resale

1. **Back up your data** before wiping
2. For most resale scenarios, DoD method is recommended:
   ```bash
   python secure_eraser.py freespace C:\ --method dod
   ```
3. For drives containing highly sensitive information, use Gutmann method:
   ```bash
   python secure_eraser.py freespace C:\ --method gutmann
   ```
4. For maximum assurance, consider using dedicated bootable wiping tools such as DBAN (Darik's Boot and Nuke) after running this tool

## Important Notes

- Wiping time increases significantly with drive size and number of passes
- SSDs require different wiping approaches than traditional hard drives
- Administrator/root privileges may be required for some operations
- For commercial or regulated environments, consider keeping a log of wiping operations for compliance purposes
