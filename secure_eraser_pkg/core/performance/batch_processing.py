"""
Batch processing capabilities for improved performance.
"""

import os
import time
import logging
import concurrent.futures
import psutil
from typing import List, Dict, Tuple, Optional, Any, Callable

class BatchProcessor:
    """
    Handles batch processing of multiple files for improved performance.
    """
    
    def __init__(self, max_workers: Optional[int] = None, logger: Optional[logging.Logger] = None):
        """
        Initialize the batch processor.
        
        Args:
            max_workers: Maximum number of parallel workers. If None, will be set to (CPU count - 1).
            logger: Logger instance to use.
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Determine optimal worker count if not specified
        if max_workers is None:
            # Use CPU count - 1, but minimum of 1
            self.max_workers = max(1, psutil.cpu_count(logical=False) or 2 - 1)
        else:
            self.max_workers = max_workers
            
        self.logger.debug(f"BatchProcessor initialized with {self.max_workers} workers")
        
        # Statistics tracking
        self.stats = {
            "total_files": 0,
            "processed_files": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None,
            "batch_stats": []
        }
    
    def process_file_list(self, 
                         files: List[str], 
                         processor_func: Callable[[str, Any], bool],
                         batch_size: Optional[int] = None, 
                         **processor_kwargs) -> Dict[str, Any]:
        """
        Process a list of files in parallel batches.
        
        Args:
            files: List of file paths to process
            processor_func: Function to call for each file (first arg must be file path)
            batch_size: Files to process per batch, default is max_workers*2
            **processor_kwargs: Additional kwargs to pass to processor_func
            
        Returns:
            Statistics dictionary with results
        """
        if not files:
            self.logger.warning("No files to process")
            return self.stats
            
        # Reset statistics
        self.stats = {
            "total_files": len(files),
            "processed_files": 0,
            "errors": 0,
            "start_time": time.time(),
            "end_time": None,
            "batch_stats": []
        }
        
        # Default batch size to double the worker count
        if batch_size is None:
            batch_size = self.max_workers * 2
        
        # Calculate number of batches
        num_batches = (len(files) + batch_size - 1) // batch_size
        
        self.logger.info(f"Processing {len(files)} files in {num_batches} batches with {self.max_workers} workers")
        
        try:
            # Process files in batches
            for i in range(0, len(files), batch_size):
                batch_files = files[i:i+batch_size]
                batch_number = i // batch_size + 1
                
                self.logger.info(f"Processing batch {batch_number}/{num_batches} ({len(batch_files)} files)")
                
                # Start timing for this batch
                batch_start = time.time()
                
                # Process the batch in parallel
                results = self._process_batch(batch_files, processor_func, **processor_kwargs)
                
                # Update statistics
                successful = sum(1 for r in results if r[1])
                failed = len(batch_files) - successful
                
                batch_stats = {
                    "batch_number": batch_number,
                    "batch_size": len(batch_files),
                    "successful": successful,
                    "failed": failed,
                    "duration": time.time() - batch_start
                }
                
                self.stats["processed_files"] += successful
                self.stats["errors"] += failed
                self.stats["batch_stats"].append(batch_stats)
                
                self.logger.info(f"Batch {batch_number} complete: {successful} succeeded, {failed} failed")
                self.logger.info(f"Progress: {self.stats['processed_files']}/{self.stats['total_files']} files processed")
        
        finally:
            # Record end time
            self.stats["end_time"] = time.time()
            
            # Calculate overall duration
            duration = self.stats["end_time"] - self.stats["start_time"]
            self.stats["duration"] = duration
            
            self.logger.info(f"Batch processing complete in {duration:.2f} seconds")
            self.logger.info(f"Processed {self.stats['processed_files']}/{self.stats['total_files']} files with {self.stats['errors']} errors")
        
        return self.stats
    
    def _process_batch(self, 
                     batch_files: List[str], 
                     processor_func: Callable[[str, Any], bool],
                     **processor_kwargs) -> List[Tuple[str, bool]]:
        """
        Process a batch of files in parallel.
        
        Args:
            batch_files: List of file paths in this batch
            processor_func: Function to call for each file
            **processor_kwargs: Additional kwargs to pass to processor_func
            
        Returns:
            List of (file_path, success) tuples
        """
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(processor_func, file_path, **processor_kwargs): file_path 
                for file_path in batch_files
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    success = future.result()
                    results.append((file_path, success))
                except Exception as e:
                    self.logger.error(f"Error processing {file_path}: {e}")
                    results.append((file_path, False))
        
        return results
    
    def process_directory_tree(self, 
                              directory_path: str,
                              processor_func: Callable[[str, Any], bool],
                              file_filter: Optional[Callable[[str], bool]] = None,
                              **processor_kwargs) -> Dict[str, Any]:
        """
        Process all files in a directory tree using batch processing.
        
        Args:
            directory_path: Root directory to process
            processor_func: Function to call for each file
            file_filter: Optional function to filter files (returns True to include)
            **processor_kwargs: Additional kwargs to pass to processor_func
            
        Returns:
            Statistics dictionary with results
        """
        if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
            self.logger.error(f"Directory {directory_path} does not exist or is not a directory.")
            return {"error": "Invalid directory"}
        
        # Collect all eligible files
        files = []
        for root, _, filenames in os.walk(directory_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                if file_filter is None or file_filter(file_path):
                    files.append(file_path)
        
        self.logger.info(f"Found {len(files)} files to process in {directory_path}")
        
        # Process the collected files
        return self.process_file_list(files, processor_func, **processor_kwargs)