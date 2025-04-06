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
from secure_eraser_pkg.core.performance.batch_processing import BatchProcessor
from secure_eraser_pkg.core.performance.resource_optimizer import ResourceOptimizer
from secure_eraser_pkg.core.performance.gpu_acceleration import GPUAccelerator
from secure_eraser_pkg.core.performance.pause_resume import JobManager, WipingJob
from secure_eraser_pkg.core.security.custom_patterns import CustomPatternManager


def parse_arguments():
    """
    Parse command-line arguments for the secure eraser tool.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Secure File Eraser - Securely erase files, directories, free space, or entire drives',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Operation type
    operation_group = parser.add_argument_group("Operations")
    operation_group.add_argument('--file', help='Securely delete a single file')
    operation_group.add_argument('--dir', help='Securely delete a directory and all its contents')
    operation_group.add_argument('--freespace', help='Wipe free space on a drive')
    operation_group.add_argument('--drive', help='Wipe an entire drive (DANGER: requires --force)')
    operation_group.add_argument('--batch', help='Process a batch of files/directories from a text file (one path per line)')
    operation_group.add_argument('--force', action='store_true', help='Force wiping of an entire drive')
    
    # Wiping method
    method_group = parser.add_argument_group("Wiping Method")
    method_group.add_argument('--passes', type=int, default=3, help='Number of overwrite passes (default: 3)')
    method_group.add_argument('--method', 
                             choices=['standard', 'dod', 'gutmann', 'paranoid', 
                                      'nist_clear', 'nist_purge', 'dod_3pass', 'dod_7pass', 
                                      'hmg_is5_baseline', 'hmg_is5_enhanced', 'navso', 
                                      'afssi', 'ar_380_19', 'csc'], 
                             default='standard', 
                             help='Wiping method: standard, dod, gutmann, paranoid, or military standards:\n'
                                  'nist_clear, nist_purge (NIST SP 800-88),\n'
                                  'dod_3pass, dod_7pass (DoD 5220.22-M variants),\n'
                                  'hmg_is5_baseline, hmg_is5_enhanced (UK Government),\n'
                                  'navso (US Navy), afssi (Air Force), ar_380_19 (Army),\n'
                                  'csc (NSA CSC-STD-005-85)\n'
                                  '(default: standard)')
    method_group.add_argument('--custom-pattern', help='Use a custom wiping pattern (name of pattern in config)')
    method_group.add_argument('--create-pattern', help='Create a new custom wiping pattern with the given name')
    method_group.add_argument('--pattern-hex', help='Hex string for custom pattern (used with --create-pattern)')
    method_group.add_argument('--delete-pattern', help='Delete a custom wiping pattern by name')
    method_group.add_argument('--list-patterns', action='store_true', help='List all available wiping patterns')
    
    # Performance options
    performance_group = parser.add_argument_group("Performance")
    performance_group.add_argument('--workers', type=int, help='Number of parallel workers for batch processing (default: auto)')
    performance_group.add_argument('--gpu', action='store_true', help='Enable GPU acceleration for wiping operations if available')
    performance_group.add_argument('--optimize-resources', action='store_true', help='Dynamically optimize resource usage based on system load')
    performance_group.add_argument('--chunk-size', type=int, help='Chunk size for wiping operations in MB (default: auto)')
    
    # Job control
    job_group = parser.add_argument_group("Job Control")
    job_group.add_argument('--job-id', help='Job ID for resuming a paused operation')
    job_group.add_argument('--list-jobs', action='store_true', help='List all available jobs')
    job_group.add_argument('--cancel-job', help='Cancel a job by ID')
    job_group.add_argument('--delete-job', help='Delete a completed job by ID')
    
    # Verification
    verification_group = parser.add_argument_group("Cryptographic Verification")
    verification_group.add_argument('--verify', action='store_true', help='Enable cryptographic verification of file wiping')
    verification_group.add_argument('--hash-algorithms', default='sha256,md5', 
                                   help='Hash algorithms to use for verification (comma-separated)')
    verification_group.add_argument('--sign-report', action='store_true', help='Digitally sign the verification report')
    verification_group.add_argument('--signature-key', help='Key to use for signing the report (optional, will generate a random key if not provided)')
    
    # Reporting
    reporting_group = parser.add_argument_group("Reporting")
    reporting_group.add_argument('--report-path', help='Path to save verification report')
    reporting_group.add_argument('--report-format', choices=['json', 'pdf', 'html'], default='json',
                               help='Format of verification report: json, pdf, or html (default: json)')
    
    # Logging
    logging_group = parser.add_argument_group("Logging")
    logging_group.add_argument('--verbose', action='store_true', help='Enable verbose output')
    logging_group.add_argument('--debug', action='store_true', help='Enable debug output (even more verbose)')
    logging_group.add_argument('--quiet', action='store_true', help='Suppress all output except errors')
    logging_group.add_argument('--log-file', help='Path to log file')
    
    # Add examples to usage
    parser.epilog = """Examples:
  # Securely delete a single file with 3 passes
  python secure_eraser.py --file /path/to/file.txt --passes 3
  
  # Securely delete a directory with 7 passes using DoD method
  python secure_eraser.py --dir /path/to/directory --method dod
  
  # Wipe free space on a drive using Gutmann method
  python secure_eraser.py --freespace /path/to/drive --method gutmann
  
  # Use military-grade wiping standards (NIST SP 800-88)
  python secure_eraser.py --file classified.doc --method nist_purge
  
  # Use Department of Defense 7-pass standard
  python secure_eraser.py --file secret.dat --method dod_7pass --verify
  
  # Create and use a custom wiping pattern
  python secure_eraser.py --create-pattern my_pattern --pattern-hex "DEADBEEF"
  python secure_eraser.py --file sensitive.txt --custom-pattern my_pattern
  
  # Securely delete a file with cryptographic verification
  python secure_eraser.py --file /path/to/file.txt --verify --report-path report.json
  
  # Create an HTML report with visualizations
  python secure_eraser.py --file /path/to/file.txt --verify --report-format html --report-path report.html
  
  # Enable digital signing of verification report
  python secure_eraser.py --file /path/to/file.txt --verify --sign-report --report-path report.pdf
  
  # Use verbose logging and save logs to a file
  python secure_eraser.py --file /path/to/file.txt --verbose --log-file eraser.log
  
  # Wipe an entire drive with NSA standard (DANGEROUS!)
  python secure_eraser.py --drive /path/to/drive --method csc --force
  
  # Process a batch of files with GPU acceleration
  python secure_eraser.py --batch file_list.txt --gpu --workers 4
  
  # List all available wiping patterns
  python secure_eraser.py --list-patterns
  
  # Resume a paused job
  python secure_eraser.py --job-id abc123def456
  
  # List all available jobs
  python secure_eraser.py --list-jobs
  """
    
    return parser.parse_args()


def handle_batch_processing(args, logger):
    """
    Handle batch processing of multiple files or directories.
    
    Args:
        args: Command-line arguments
        logger: Logger instance
        
    Returns:
        True if successful, False otherwise
    """
    if not os.path.exists(args.batch):
        logger.error(f"Batch file {args.batch} not found")
        return False
    
    # Read paths from the batch file
    try:
        with open(args.batch, 'r') as f:
            paths = [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Error reading batch file: {e}")
        return False
    
    logger.info(f"Loaded {len(paths)} paths from {args.batch}")
    
    # Initialize batch processor
    batch_processor = BatchProcessor(max_workers=args.workers, logger=logger)
    
    # Create eraser instance
    hash_algorithms = [algo.strip() for algo in args.hash_algorithms.split(',')]
    eraser = SecureEraserWithVerification(
        passes=args.passes,
        method=args.method,
        verify=args.verify,
        hash_algorithms=hash_algorithms,
        logger=logger
    )
    
    # Enable GPU acceleration if requested
    if args.gpu:
        gpu_accelerator = GPUAccelerator(logger=logger)
        if gpu_accelerator.is_available:
            logger.info(f"GPU acceleration enabled: {gpu_accelerator.device_info.get('name', 'Unknown GPU')}")
        else:
            logger.warning("GPU acceleration requested but not available, using CPU only")
    
    # Enable resource optimization if requested
    if args.optimize_resources:
        resource_optimizer = ResourceOptimizer(logger=logger)
        optimization_params = resource_optimizer.get_optimization_params()
        logger.info(f"Resource optimization enabled: {optimization_params['optimizations']}")
        
        # Apply optimizations
        chunk_size = optimization_params["optimizations"]["chunk_size"]
        if args.chunk_size:
            chunk_size = args.chunk_size * 1024 * 1024  # Convert MB to bytes
    
    # Process files and directories
    logger.info(f"Starting batch processing with {args.passes} passes using {args.method} method")
    
    # Create separate lists for files and directories
    files = [p for p in paths if os.path.isfile(p)]
    dirs = [p for p in paths if os.path.isdir(p)]
    
    result = True
    
    # Process files
    if files:
        logger.info(f"Processing {len(files)} files")
        file_stats = batch_processor.process_file_list(files, eraser.secure_delete_file)
        logger.info(f"File processing complete: {file_stats['processed_files']}/{file_stats['total_files']} files processed successfully")
        result = result and (file_stats["errors"] == 0)
    
    # Process directories
    if dirs:
        logger.info(f"Processing {len(dirs)} directories")
        dir_stats = batch_processor.process_file_list(dirs, eraser.secure_delete_directory)
        logger.info(f"Directory processing complete: {dir_stats['processed_files']}/{dir_stats['total_files']} directories processed successfully")
        result = result and (dir_stats["errors"] == 0)
    
    return result


def handle_pattern_operations(args, logger):
    """
    Handle pattern-related operations (create, list, delete).
    
    Args:
        args: Command-line arguments
        logger: Logger instance
        
    Returns:
        True if an operation was handled, False otherwise
    """
    # Check if we need to handle pattern operations
    if not any([args.create_pattern, args.delete_pattern, args.list_patterns]):
        return False
        
    try:
        # Initialize the custom patterns handler
        patterns = CustomPatternManager(logger=logger)
        
        if args.list_patterns:
            # List all available patterns
            all_patterns = patterns.format_patterns_list()
            
            print("\nAvailable Wiping Patterns:")
            print("--------------------------")
            
            # First list built-in methods
            print("\nBuilt-in Methods:")
            print("  - standard: Standard Random Data (default)")
            print("  - dod: DoD 5220.22-M (3-pass)")
            print("  - gutmann: Gutmann 35-pass Method")
            print("  - paranoid: Paranoid Enhanced Method")
            
            # Then list military standards
            print("\nMilitary Standards:")
            print("  - nist_clear: NIST SP 800-88 Clear (1-pass zeros)")
            print("  - nist_purge: NIST SP 800-88 Purge (1-pass ones)")
            print("  - dod_3pass: DoD 5220.22-M (3-pass)")
            print("  - dod_7pass: DoD 5220.22-M (7-pass)")
            print("  - hmg_is5_baseline: HMG IS5 Baseline (UK Government)")
            print("  - hmg_is5_enhanced: HMG IS5 Enhanced (UK Government)")
            print("  - navso: NAVSO P-5239-26 (US Navy)")
            print("  - afssi: AFSSI 5020 (Air Force)")
            print("  - ar_380_19: AR 380-19 (Army)")
            print("  - csc: CSC-STD-005-85 (NSA)")
            
            # List available generators for custom patterns
            generators = patterns.get_available_generators()
            print("\nAvailable Pattern Generators:")
            for gen_name, gen_desc in generators.items():
                print(f"  - {gen_name}: {gen_desc}")
            
            # List custom patterns if any
            if all_patterns:
                print("\nCustom Patterns:")
                for name, info in all_patterns.items():
                    if info['type'] == 'bytes':
                        print(f"  - {name}: {info['description'] or 'Custom byte pattern'} ({info['size']} bytes)")
                        print(f"    Preview: {info['preview']}")
                    else:
                        print(f"  - {name}: {info['description'] or 'Multi-pass pattern'} ({info['passes']} passes)")
                        
            else:
                print("\nNo custom patterns defined.")
                
            print("\nUse --create-pattern to add a new custom pattern.")
            return True
            
        elif args.create_pattern:
            # Create a new custom pattern
            if not args.pattern_hex:
                logger.error("To create a custom pattern, you must provide a hex string with --pattern-hex")
                return True
                
            pattern_name = args.create_pattern
            pattern_hex = args.pattern_hex
            
            # Try to create the pattern
            success = patterns.create_hex_pattern(pattern_name, pattern_hex, 
                                                 description=f"Custom pattern created on {time.ctime()}")
            
            if success:
                logger.info(f"Custom pattern '{pattern_name}' created successfully")
                print(f"Pattern '{pattern_name}' created. Use --custom-pattern {pattern_name} to use it.")
            else:
                logger.error(f"Failed to create custom pattern '{pattern_name}'")
                
            return True
            
        elif args.delete_pattern:
            # Delete a custom pattern
            pattern_name = args.delete_pattern
            
            # Try to delete the pattern
            success = patterns.delete_pattern(pattern_name)
            
            if success:
                logger.info(f"Custom pattern '{pattern_name}' deleted successfully")
            else:
                logger.error(f"Failed to delete pattern '{pattern_name}'. Pattern not found.")
                
            return True
            
    except ImportError as e:
        logger.error(f"Error loading custom patterns module: {e}")
        return True
    except Exception as e:
        logger.error(f"Error handling pattern operations: {e}")
        return True
        
    return False


def handle_job_operations(args, logger):
    """
    Handle job-related operations (list, resume, cancel, delete).
    
    Args:
        args: Command-line arguments
        logger: Logger instance
        
    Returns:
        True if an operation was handled, False otherwise
    """
    # Initialize job manager
    job_manager = JobManager(logger=logger)
    
    if args.list_jobs:
        # List all available jobs
        jobs = job_manager.list_jobs()
        
        if not jobs:
            print("No wiping jobs found")
            return True
        
        print(f"Found {len(jobs)} wiping jobs:")
        for i, job in enumerate(jobs):
            # Format timestamps for display
            created = job["created_at"]
            updated = job["updated_at"]
            
            # Format progress info
            progress_str = ""
            if "progress" in job and job["progress"]["total_items"] > 0:
                progress_pct = (job["progress"]["processed_items"] / job["progress"]["total_items"]) * 100
                progress_str = f" - Progress: {progress_pct:.1f}%"
            
            print(f"{i+1}. Job ID: {job['job_id']} - Status: {job['status']}{progress_str}")
            print(f"   Created: {created}, Last updated: {updated}")
            print()
        
        return True
        
    elif args.job_id:
        # Resume a job
        job = job_manager.load_job(args.job_id)
        
        if not job:
            logger.error(f"Job {args.job_id} not found")
            return True
        
        if job.status != WipingJob.STATUS_PAUSED:
            logger.error(f"Job {args.job_id} is not paused (status: {job.status})")
            return True
        
        logger.info(f"Resuming job {args.job_id}")
        
        # Resume the job
        job.start()
        
        # Extract job config and create appropriate eraser
        # This would need to handle the specific job type and operation
        
        # For now, just print job details
        print(f"Job {args.job_id} details:")
        print(f"Status: {job.status}")
        print(f"Progress: {job.progress['processed_items']}/{job.progress['total_items']} items")
        print()
        print("Job resumption not fully implemented yet")
        
        return True
        
    elif args.cancel_job:
        # Cancel a job
        job = job_manager.load_job(args.cancel_job)
        
        if not job:
            logger.error(f"Job {args.cancel_job} not found")
            return True
        
        if job.status not in [WipingJob.STATUS_RUNNING, WipingJob.STATUS_PAUSED]:
            logger.error(f"Job {args.cancel_job} cannot be cancelled (status: {job.status})")
            return True
        
        # Cancel the job
        job.cancel()
        logger.info(f"Job {args.cancel_job} cancelled")
        
        return True
        
    elif args.delete_job:
        # Delete a job
        if job_manager.delete_job(args.delete_job):
            logger.info(f"Job {args.delete_job} deleted")
        else:
            logger.error(f"Failed to delete job {args.delete_job}")
        
        return True
    
    return False


def main():
    """
    Main entry point for the Secure Eraser tool.
    """
    # Parse command-line arguments
    args = parse_arguments()
    parser = argparse.ArgumentParser()  # Define parser for access in error case
    
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
    
    # Handle pattern operations first
    if handle_pattern_operations(args, logger):
        # A pattern operation was performed, no need for further processing
        return 0
    
    # Handle job operations next
    if handle_job_operations(args, logger):
        # A job operation was performed, no need for further processing
        return 0
    
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
    
    # Enable GPU acceleration if requested
    if args.gpu:
        gpu_accelerator = GPUAccelerator(logger=logger)
        if gpu_accelerator.is_available:
            logger.info(f"GPU acceleration enabled: {gpu_accelerator.device_info.get('name', 'Unknown GPU')}")
        else:
            logger.warning("GPU acceleration requested but not available, using CPU only")
    
    # Enable resource optimization if requested
    if args.optimize_resources:
        resource_optimizer = ResourceOptimizer(logger=logger)
        optimization_params = resource_optimizer.get_optimization_params()
        logger.info(f"Resource optimization enabled: {optimization_params['optimizations']}")
    
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
            
        if args.gpu:
            print(f"- GPU Acceleration: {'Enabled' if gpu_accelerator.is_available else 'Disabled (not available)'}")
            
        if args.optimize_resources:
            print(f"- Resource Optimization: Enabled")
            print(f"  - Chunk Size: {optimization_params['optimizations']['chunk_size'] // (1024*1024)} MB")
            print(f"  - Workers: {optimization_params['optimizations']['max_workers']}")
            
        print()
    
    # Check that only one operation was specified
    operations = sum(1 for op in [args.file, args.dir, args.freespace, args.drive, args.batch] if op)
    if operations != 1:
        logger.error("Please specify exactly one operation type (--file, --dir, --freespace, --drive, or --batch)")
        parser.print_help()
        return 1
    
    # Perform the requested operation
    start_time = time.time()
    
    if args.file:
        if not os.path.exists(args.file):
            logger.error(f"File {args.file} does not exist")
            return 1
            
        logger.info(f"Securely deleting file: {args.file}")
        success = eraser.secure_delete_file(args.file)
        
    elif args.dir:
        if not os.path.exists(args.dir):
            logger.error(f"Directory {args.dir} does not exist")
            return 1
            
        logger.info(f"Securely deleting directory: {args.dir}")
        success = eraser.secure_delete_directory(args.dir)
        
    elif args.freespace:
        if not os.path.exists(args.freespace):
            logger.error(f"Drive {args.freespace} does not exist")
            return 1
            
        logger.info(f"Wiping free space on: {args.freespace}")
        success = eraser.wipe_free_space(args.freespace)
        
    elif args.drive:
        if not os.path.exists(args.drive):
            logger.error(f"Drive {args.drive} does not exist")
            return 1
            
        if not args.force:
            logger.error(f"To wipe an entire drive, you must use the --force flag")
            return 1
            
        logger.warning(f"DANGER: Wiping entire drive: {args.drive}")
        print(f"You are about to PERMANENTLY ERASE ALL DATA on {args.drive}")
        print("This cannot be undone. Type 'YES' to continue:")
        
        confirmation = input()
        if confirmation.upper() != "YES":
            logger.info("Operation cancelled by user")
            return 1
            
        logger.info(f"Wiping entire drive: {args.drive}")
        success = eraser.wipe_drive(args.drive)
        
    elif args.batch:
        logger.info(f"Processing batch from file: {args.batch}")
        success = handle_batch_processing(args, logger)
        
    else:
        logger.error("No operation specified")
        parser.print_help()
        return 1
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    logger.info(f"Operation completed in {elapsed_time:.2f} seconds")
    
    # Generate report if requested
    if args.verify and args.report_path and hasattr(eraser, 'verification_data'):
        try:
            # Add system and performance information to the report
            report_data = eraser.verification_data
            
            # Get system information for the report
            from secure_eraser_pkg.utils.system_info import get_system_info
            system_info = get_system_info()
            
            # Generate the report
            # Prepare signature info if signing was requested
            signature_info = None
            if hasattr(args, 'sign_report') and args.sign_report:
                signature_info = {
                    "signed": True,
                    "key": args.signature_key.encode() if hasattr(args, 'signature_key') and args.signature_key else None
                }
                
            report_file = generate_report(
                args.report_format,
                report_data,
                args.report_path,
                signature=signature_info,
                system_info=system_info
            )
            
            logger.info(f"Report saved to {report_file}")
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())