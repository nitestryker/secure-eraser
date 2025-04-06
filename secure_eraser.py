#!/usr/bin/env python
"""
Secure Eraser Tool - Cryptographically secure file erasure utility

A tool for securely erasing files, directories, free space, and entire drives
using various secure deletion methods with cryptographic verification.

For usage instructions, run:
    python secure_eraser.py --help
"""

import sys
from secure_eraser_pkg.cli import main

if __name__ == "__main__":
    sys.exit(main())