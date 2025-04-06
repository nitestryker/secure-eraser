"""
Command-line interface for the Secure Eraser tool.
"""

import argparse
import logging
import sys
import os
import time
from typing import Dict, List, Optional, Union

from secure_eraser_pkg.core import SecureEraserWithVerification
from secure_eraser_pkg.utils.logging_setup import setup_logging
from secure_eraser_pkg.reporting import generate_report


def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments object
    """
    parser = argparse.ArgumentParser(
        description="Secure File Eraser - Securely erase files, directories, free space, or entire drives",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Operations group
    operations_group = parser.add_argument_group('Operations')
    operations_group.add_argument('--file', help='Securely delete a single file')
    operations_group.add_argument('--dir', help='Securely delete a directory and all its contents')
    operations_group.add_argument('--freespace', help='Wipe free space on a drive')
    operations_group.add_argument('--drive', help='Wipe an entire drive (DANGER: requires --force)')
    operations_group.add_argument('--force', action='store_true', help='Force wiping of an entire drive')
    
    # Wiping method group
    method_group = parser.add_argument_group('Wiping Method')
    method_group.add_argument('--passes', type=int, default=3, help='Number of overwrite passes (default: 3)')
    method_group.add_argument('--method', choices=['standard', 'dod', 'gutmann', 'paranoid'], 
                            default='standard', help='Wiping method: standard, dod, gutmann, or paranoid (default: standard)')
    
    # Cryptographic verification group
    verify_group = parser.add_argument_group('Cryptographic Verification')
    verify_group.add_argument('--verify', action='store_true', help='Enable cryptographic verification of file wiping')
    verify_group.add_argument('--hash-algorithms', help='Hash algorithms to use for verification (comma-separated)')
    verify_group.add_argument('--sign-report', action='store_true', help='Digitally sign the verification report')
    verify_group.add_argument('--signature-key', help='Key to use for signing the report (optional, will generate a random key if not provided)')
    
    # Reporting group
    report_group = parser.add_argument_group('Reporting')
    report_group.add_argument('--report-path', help='Path to save verification report')
    report_group.add_argument('--report-format', choices=['json', 'pdf', 'html'], default='json',
                            help='Format of verification report: json, pdf, or html (default: json)')
    
    # Logging group
    logging_group = parser.add_argument_group('Logging')
    logging_group.add_argument('--verbose', action='store_true', help='Enable verbose output')
    logging_group.add_argument('--debug', action='store_true', help='Enable debug output (even more verbose)')
    logging_group.add_argument('--quiet', action='store_true', help='Suppress all output except errors')
    logging_group.add_argument('--log-file', help='Path to log file')
    
    # Add examples to the help text
    parser.epilog = """Examples:
  # Securely delete a single file with 3 passes
  python secure_eraser.py --file /path/to/file.txt --passes 3
  
  # Securely delete a directory with 7 passes using DoD method
  python secure_eraser.py --dir /path/to/directory --method dod
  
  # Wipe free space on a drive using Gutmann method
  python secure_eraser.py --freespace /path/to/drive --method gutmann
  
  # Securely delete a file with cryptographic verification
  python secure_eraser.py --file /path/to/file.txt --verify --report-path report.json
  
  # Create an HTML report with visualizations
  python secure_eraser.py --file /path/to/file.txt --verify --report-format html --report-path report.html
  
  # Enable digital signing of verification report
  python secure_eraser.py --file /path/to/file.txt --verify --sign-report --report-path report.pdf
  
  # Use verbose logging and save logs to a file
  python secure_eraser.py --file /path/to/file.txt --verbose --log-file eraser.log
  
  # Wipe an entire drive (DANGEROUS!)
  python secure_eraser.py --drive /path/to/drive --method paranoid --force
        """
    
    return parser.parse_args()


def main():
    """
    Main entry point for the Secure Eraser tool.
    """
    # Parse command-line arguments
    args = parse_arguments()
    parser = argparse.ArgumentParser() # Define parser for access in error case
    
    # Determine log level
    if args.debug:
        log_level = logging.DEBUG
    elif args.verbose:
        log_level = logging.INFO
    elif args.quiet:
        log_level = logging.ERROR
    else:
        log_level = logging.INFO
    
    # Set up logging
    logger = setup_logging(log_level, args.log_file)
    
    # Parse hash algorithms if specified
    hash_algorithms = None
    if args.hash_algorithms:
        hash_algorithms = [algo.strip() for algo in args.hash_algorithms.split(',')]
    
    # Create secure eraser instance
    eraser = SecureEraserWithVerification(
        passes=args.passes,
        method=args.method,
        verify=args.verify,
        hash_algorithms=hash_algorithms,
        logger=logger
    )
    
    # Show settings
    if not args.quiet:
        print("Secure Eraser Settings:")
        print(f"- Method: {args.method.upper()}")
        print(f"- Passes: {args.passes}")
        print(f"- Verification: {'Enabled' if args.verify else 'Disabled'}")
        
        if args.verify and hash_algorithms:
            print(f"- Hash Algorithms: {', '.join(hash_algorithms)}")
        elif args.verify:
            print(f"- Hash Algorithms: {', '.join(eraser.hash_algorithms)}")
            
        if args.report_path:
            print(f"- Report Path: {args.report_path} ({args.report_format.upper()})")
    
    # Perform the requested operation
    start_time = time.time()
    success = False
    
    if args.file:
        success = eraser.secure_delete_file(args.file)
    elif args.dir:
        success = eraser.secure_delete_directory(args.dir)
    elif args.freespace:
        success = eraser.wipe_free_space(args.freespace)
    elif args.drive:
        success = eraser.wipe_entire_drive(args.drive, args.force)
    else:
        logger.error("No operation specified. Use --file, --dir, --freespace, or --drive.")
        parser.print_help()
        sys.exit(1)
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    if not args.quiet:
        print(f"\nOperation completed in {elapsed_time:.2f} seconds")
    
    # Generate verification report if requested
    if args.verify and args.report_path:
        try:
            # Prepare report data
            report_data = {
                "timestamp": eraser.verification_data["timestamp"],
                "wiping_method": eraser.method,
                "passes": eraser.passes,
                "verification_enabled": eraser.verify,
                "hash_algorithms": eraser.hash_algorithms,
                "items": eraser.verification_data["wiped_items"],
                "system_info": eraser.system_info,
                "performance_stats": eraser.performance_stats
            }
            
            # Sign report if requested
            signature = None
            if args.sign_report:
                signature = eraser.sign_data(report_data, args.signature_key)
            
            # Generate report
            generate_report(
                args.report_format,
                report_data,
                args.report_path,
                signature,
                eraser.system_info
            )
            
            if not args.quiet:
                print(f"Verification report saved to: {args.report_path}")
                
                # Show verification summary
                verified_count = sum(1 for item in eraser.verification_data["wiped_items"] 
                                    if item["verification"]["verified"])
                total_count = len(eraser.verification_data["wiped_items"])
                
                if total_count > 0:
                    percent = (verified_count / total_count) * 100
                    print(f"Verification Summary: {verified_count}/{total_count} items verified successfully ({percent:.1f}%)")
                
        except Exception as e:
            logger.error(f"Error generating report: {e}")
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()