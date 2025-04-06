"""
Pause/resume capabilities for SecureEraser.

This module enables pausing and resuming long-running wiping operations,
allowing users to stop and restart wiping operations without losing progress.
"""

import os
import json
import time
import logging
import tempfile
import uuid
import datetime
import signal
from typing import Dict, List, Optional, Any, Callable, Union, Tuple


class WipingJob:
    """
    Represents a wiping job that can be paused and resumed.
    """
    
    STATUS_PENDING = "pending"
    STATUS_RUNNING = "running"
    STATUS_PAUSED = "paused"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    STATUS_CANCELED = "canceled"
    
    def __init__(self, job_id: Optional[str] = None, 
                 logger: Optional[logging.Logger] = None):
        """
        Initialize a wiping job.
        
        Args:
            job_id: Unique ID for this job (will be generated if not provided)
            logger: Logger instance to use
        """
        self.job_id = job_id or str(uuid.uuid4())
        self.logger = logger or logging.getLogger(__name__)
        
        # Job metadata
        self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = self.created_at
        self.status = self.STATUS_PENDING
        
        # Job configuration
        self.config = {}
        
        # Progress tracking
        self.progress = {
            "total_items": 0,
            "processed_items": 0,
            "current_item": None,
            "current_item_progress": 0,
            "current_pass": 0,
            "total_passes": 0,
            "bytes_processed": 0,
            "bytes_total": 0,
            "start_time": None,
            "end_time": None,
            "pause_time": None,
            "resume_time": None,
            "paused_duration": 0,
            "estimated_time_remaining": None
        }
        
        # Result tracking
        self.results = {
            "success_count": 0,
            "error_count": 0,
            "errors": []
        }
        
        # Checkpointing
        self.checkpoint = {
            "last_checkpoint": None,
            "checkpoint_file": None,
            "completed_items": [],
            "skipped_items": []
        }
        
        # Register signal handlers for graceful shutdown
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """
        Set up signal handlers to handle interruptions gracefully.
        """
        # Define a signal handler
        def handle_signal(sig, frame):
            self.logger.warning(f"Received signal {sig}, pausing job {self.job_id}")
            self.pause()
            
        # Register the handler for common termination signals
        for sig in [signal.SIGINT, signal.SIGTERM]:
            try:
                # Only set if we're in the main thread to avoid issues
                if not signal.getsignal(sig) == signal.SIG_IGN:
                    signal.signal(sig, handle_signal)
            except (ValueError, AttributeError):
                self.logger.debug(f"Could not set signal handler for {sig}")
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the wiping job.
        
        Args:
            config: Configuration dictionary for this job
        """
        self.config = config
        
        # Extract passes and method from config if available
        if "method" in config:
            self.progress["method"] = config["method"]
        if "passes" in config:
            self.progress["total_passes"] = config["passes"]
        
        # Update timestamp
        self.updated_at = datetime.datetime.now().isoformat()
    
    def start(self) -> None:
        """
        Start the wiping job.
        """
        # Set status to running
        self.status = self.STATUS_RUNNING
        
        # Record start time if this is the first start
        if not self.progress["start_time"]:
            self.progress["start_time"] = datetime.datetime.now().isoformat()
            
        # If this is a resume, record resume time
        if self.progress["pause_time"]:
            self.progress["resume_time"] = datetime.datetime.now().isoformat()
            
            # Calculate and accumulate paused duration
            pause_dt = datetime.datetime.fromisoformat(self.progress["pause_time"])
            resume_dt = datetime.datetime.fromisoformat(self.progress["resume_time"])
            pause_duration = (resume_dt - pause_dt).total_seconds()
            self.progress["paused_duration"] += pause_duration
            
            # Clear pause time
            self.progress["pause_time"] = None
        
        # Update timestamp
        self.updated_at = datetime.datetime.now().isoformat()
        
        # Save checkpoint
        self.save_checkpoint()
        
        self.logger.info(f"Job {self.job_id} started/resumed")
    
    def pause(self) -> None:
        """
        Pause the wiping job.
        """
        # Only pause if we're running
        if self.status != self.STATUS_RUNNING:
            return
            
        # Set status to paused
        self.status = self.STATUS_PAUSED
        
        # Record pause time
        self.progress["pause_time"] = datetime.datetime.now().isoformat()
        
        # Update timestamp
        self.updated_at = datetime.datetime.now().isoformat()
        
        # Save checkpoint
        self.save_checkpoint()
        
        self.logger.info(f"Job {self.job_id} paused")
    
    def complete(self, success: bool = True) -> None:
        """
        Mark the wiping job as completed.
        
        Args:
            success: Whether the job completed successfully
        """
        # Set status based on success
        self.status = self.STATUS_COMPLETED if success else self.STATUS_FAILED
        
        # Record end time
        self.progress["end_time"] = datetime.datetime.now().isoformat()
        
        # Calculate duration
        if self.progress["start_time"]:
            start_dt = datetime.datetime.fromisoformat(self.progress["start_time"])
            end_dt = datetime.datetime.fromisoformat(self.progress["end_time"])
            duration = (end_dt - start_dt).total_seconds() - self.progress["paused_duration"]
            self.progress["duration"] = duration
        
        # Update timestamp
        self.updated_at = datetime.datetime.now().isoformat()
        
        # Save final checkpoint
        self.save_checkpoint()
        
        self.logger.info(f"Job {self.job_id} completed with status: {self.status}")
    
    def cancel(self) -> None:
        """
        Cancel the wiping job.
        """
        # Set status to canceled
        self.status = self.STATUS_CANCELED
        
        # Record end time
        self.progress["end_time"] = datetime.datetime.now().isoformat()
        
        # Update timestamp
        self.updated_at = datetime.datetime.now().isoformat()
        
        # Save final checkpoint
        self.save_checkpoint()
        
        self.logger.info(f"Job {self.job_id} canceled")
    
    def update_progress(self, progress_update: Dict[str, Any]) -> None:
        """
        Update the progress of the wiping job.
        
        Args:
            progress_update: Dictionary with progress updates
        """
        # Update progress with provided values
        for key, value in progress_update.items():
            if key in self.progress:
                self.progress[key] = value
        
        # Calculate estimated time remaining if we have enough data
        if (self.progress["total_items"] > 0 and 
            self.progress["processed_items"] > 0 and
            self.progress["start_time"] and
            not self.progress["end_time"]):
            
            start_dt = datetime.datetime.fromisoformat(self.progress["start_time"])
            now_dt = datetime.datetime.now()
            
            # Calculate elapsed time, excluding paused time
            elapsed = (now_dt - start_dt).total_seconds() - self.progress["paused_duration"]
            
            if elapsed > 0:
                # Calculate progress percentage
                progress_pct = self.progress["processed_items"] / self.progress["total_items"]
                
                if progress_pct > 0:
                    # Calculate estimated total time and remaining time
                    estimated_total = elapsed / progress_pct
                    remaining = estimated_total - elapsed
                    
                    # Store estimated time remaining
                    if remaining > 0:
                        self.progress["estimated_time_remaining"] = remaining
        
        # Update timestamp
        self.updated_at = datetime.datetime.now().isoformat()
        
        # Periodically save checkpoint (every 5% progress)
        if self.progress["total_items"] > 0:
            old_pct = int((self.progress["processed_items"] - 1) / self.progress["total_items"] * 20)
            new_pct = int(self.progress["processed_items"] / self.progress["total_items"] * 20)
            
            if new_pct > old_pct:
                self.save_checkpoint()
    
    def add_error(self, item: str, error: str) -> None:
        """
        Add an error to the job results.
        
        Args:
            item: The item (file/directory) that had an error
            error: Error message
        """
        # Increment error count
        self.results["error_count"] += 1
        
        # Add error details
        self.results["errors"].append({
            "item": item,
            "error": error,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        # Update timestamp
        self.updated_at = datetime.datetime.now().isoformat()
    
    def add_success(self, item: str) -> None:
        """
        Add a successful item to the job results.
        
        Args:
            item: The item (file/directory) that was successfully processed
        """
        # Increment success count
        self.results["success_count"] += 1
        
        # Add to completed items for checkpointing
        self.checkpoint["completed_items"].append(item)
        
        # Update timestamp
        self.updated_at = datetime.datetime.now().isoformat()
    
    def is_item_completed(self, item: str) -> bool:
        """
        Check if an item has already been completed.
        
        Args:
            item: The item (file/directory) to check
            
        Returns:
            True if the item has been completed, False otherwise
        """
        return item in self.checkpoint["completed_items"]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the job to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the job
        """
        return {
            "job_id": self.job_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status,
            "config": self.config,
            "progress": self.progress,
            "results": self.results,
            "checkpoint": {
                "last_checkpoint": self.checkpoint["last_checkpoint"],
                "checkpoint_file": self.checkpoint["checkpoint_file"],
                "completed_items_count": len(self.checkpoint["completed_items"]),
                "skipped_items_count": len(self.checkpoint["skipped_items"])
            }
        }
    
    def save_checkpoint(self) -> str:
        """
        Save the current job state to a checkpoint file.
        
        Returns:
            Path to the checkpoint file
        """
        # Create a checkpoint file if we don't have one yet
        if not self.checkpoint["checkpoint_file"]:
            checkpoint_dir = os.path.join(tempfile.gettempdir(), "secure_eraser_checkpoints")
            os.makedirs(checkpoint_dir, exist_ok=True)
            
            checkpoint_file = os.path.join(checkpoint_dir, f"job_{self.job_id}.json")
            self.checkpoint["checkpoint_file"] = checkpoint_file
        
        # Prepare data for serialization
        checkpoint_data = {
            "job_id": self.job_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status,
            "config": self.config,
            "progress": self.progress,
            "results": self.results,
            "checkpoint": {
                "last_checkpoint": datetime.datetime.now().isoformat(),
                "completed_items": self.checkpoint["completed_items"],
                "skipped_items": self.checkpoint["skipped_items"]
            }
        }
        
        # Save to file
        try:
            with open(self.checkpoint["checkpoint_file"], 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
                
            # Update last checkpoint time
            self.checkpoint["last_checkpoint"] = checkpoint_data["checkpoint"]["last_checkpoint"]
            
            self.logger.debug(f"Saved checkpoint to {self.checkpoint['checkpoint_file']}")
            return self.checkpoint["checkpoint_file"]
            
        except Exception as e:
            self.logger.error(f"Error saving checkpoint: {e}")
            return ""
    
    @classmethod
    def load_from_checkpoint(cls, checkpoint_file: str, 
                           logger: Optional[logging.Logger] = None) -> 'WipingJob':
        """
        Load a job from a checkpoint file.
        
        Args:
            checkpoint_file: Path to the checkpoint file
            logger: Logger instance to use
            
        Returns:
            Loaded WipingJob instance
        """
        logger = logger or logging.getLogger(__name__)
        
        try:
            # Load from file
            with open(checkpoint_file, 'r') as f:
                checkpoint_data = json.load(f)
            
            # Create a new job instance
            job = cls(job_id=checkpoint_data["job_id"], logger=logger)
            
            # Restore job state
            job.created_at = checkpoint_data["created_at"]
            job.updated_at = checkpoint_data["updated_at"]
            job.status = checkpoint_data["status"]
            job.config = checkpoint_data["config"]
            job.progress = checkpoint_data["progress"]
            job.results = checkpoint_data["results"]
            
            # Restore checkpoint data
            job.checkpoint["last_checkpoint"] = checkpoint_data["checkpoint"]["last_checkpoint"]
            job.checkpoint["checkpoint_file"] = checkpoint_file
            job.checkpoint["completed_items"] = checkpoint_data["checkpoint"]["completed_items"]
            job.checkpoint["skipped_items"] = checkpoint_data["checkpoint"]["skipped_items"]
            
            logger.info(f"Loaded job {job.job_id} from checkpoint {checkpoint_file}")
            return job
            
        except Exception as e:
            logger.error(f"Error loading checkpoint {checkpoint_file}: {e}")
            # Return a new job
            return cls(logger=logger)


class JobManager:
    """
    Manages wiping jobs, including creating, loading, and listing jobs.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the job manager.
        
        Args:
            logger: Logger instance to use
        """
        self.logger = logger or logging.getLogger(__name__)
        self.checkpoint_dir = os.path.join(tempfile.gettempdir(), "secure_eraser_checkpoints")
        
        # Ensure checkpoint directory exists
        os.makedirs(self.checkpoint_dir, exist_ok=True)
    
    def create_job(self, config: Optional[Dict[str, Any]] = None) -> WipingJob:
        """
        Create a new wiping job.
        
        Args:
            config: Configuration for the job
            
        Returns:
            New WipingJob instance
        """
        # Create a new job
        job = WipingJob(logger=self.logger)
        
        # Configure if config is provided
        if config:
            job.configure(config)
        
        self.logger.info(f"Created new job {job.job_id}")
        return job
    
    def list_jobs(self) -> List[Dict[str, Any]]:
        """
        List all available wiping jobs.
        
        Returns:
            List of job summaries
        """
        jobs = []
        
        # Find all checkpoint files
        for filename in os.listdir(self.checkpoint_dir):
            if filename.startswith("job_") and filename.endswith(".json"):
                checkpoint_file = os.path.join(self.checkpoint_dir, filename)
                
                try:
                    # Load basic job info without loading the full job
                    with open(checkpoint_file, 'r') as f:
                        checkpoint_data = json.load(f)
                    
                    # Create a job summary
                    job_summary = {
                        "job_id": checkpoint_data["job_id"],
                        "created_at": checkpoint_data["created_at"],
                        "updated_at": checkpoint_data["updated_at"],
                        "status": checkpoint_data["status"],
                        "checkpoint_file": checkpoint_file
                    }
                    
                    # Add progress info if available
                    if "progress" in checkpoint_data:
                        job_summary["progress"] = {
                            "processed_items": checkpoint_data["progress"].get("processed_items", 0),
                            "total_items": checkpoint_data["progress"].get("total_items", 0),
                            "start_time": checkpoint_data["progress"].get("start_time"),
                            "end_time": checkpoint_data["progress"].get("end_time")
                        }
                    
                    jobs.append(job_summary)
                    
                except Exception as e:
                    self.logger.warning(f"Error reading checkpoint file {checkpoint_file}: {e}")
        
        # Sort by updated_at (newest first)
        jobs.sort(key=lambda j: j["updated_at"], reverse=True)
        
        self.logger.debug(f"Found {len(jobs)} wiping jobs")
        return jobs
    
    def load_job(self, job_id: str) -> Optional[WipingJob]:
        """
        Load a wiping job by ID.
        
        Args:
            job_id: ID of the job to load
            
        Returns:
            Loaded WipingJob instance or None if not found
        """
        # Try to find the checkpoint file
        checkpoint_file = os.path.join(self.checkpoint_dir, f"job_{job_id}.json")
        
        if os.path.exists(checkpoint_file):
            # Load the job from the checkpoint
            return WipingJob.load_from_checkpoint(checkpoint_file, self.logger)
        else:
            self.logger.warning(f"No checkpoint file found for job {job_id}")
            return None
    
    def delete_job(self, job_id: str) -> bool:
        """
        Delete a wiping job.
        
        Args:
            job_id: ID of the job to delete
            
        Returns:
            True if successful, False otherwise
        """
        # Try to find the checkpoint file
        checkpoint_file = os.path.join(self.checkpoint_dir, f"job_{job_id}.json")
        
        if os.path.exists(checkpoint_file):
            try:
                # Delete the checkpoint file
                os.remove(checkpoint_file)
                self.logger.info(f"Deleted job {job_id}")
                return True
            except Exception as e:
                self.logger.error(f"Error deleting job {job_id}: {e}")
                return False
        else:
            self.logger.warning(f"No checkpoint file found for job {job_id}")
            return False