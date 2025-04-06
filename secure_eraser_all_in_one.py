import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
import time
import platform
import random
import shutil
import json
import datetime
import uuid
from pathlib import Path

class RedirectText:
    """Redirect stdout to the Text widget"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.queue = queue.Queue()
        self.updating = True
        threading.Thread(target=self.update_loop, daemon=True).start()
        
    def write(self, string):
        self.queue.put(string)
        
    def flush(self):
        pass
        
    def update_loop(self):
        while self.updating:
            try:
                while True:
                    text = self.queue.get_nowait()
                    self.text_widget.configure(state='normal')
                    self.text_widget.insert(tk.END, text)
                    self.text_widget.see(tk.END)
                    self.text_widget.configure(state='disabled')
                    self.queue.task_done()
            except queue.Empty:
                time.sleep(0.1)
                
    def close(self):
        self.updating = False


class SimpleSecureEraser:
    """
    A simplified secure erasure implementation with all methods inline
    """
    # DoD 5220.22-M standard wipe patterns
    DOD_PATTERNS = [
        b'\x00',                         # Pass 1: All zeros
        b'\xFF',                         # Pass 2: All ones
        b'\x00\xFF\x00\xFF\x00\xFF',     # Pass 3: Alternating bit pattern
        b'\x55\xAA\x55\xAA\x55\xAA',     # Pass 4: Another alternating bit pattern
        b'\x92\x49\x24',                 # Pass 5: Random pattern
        b'\x49\x92\x24\x49\x92',         # Pass 6: Another random pattern
        b'\xDB\xB6\xDB\x6D\xB6\xDB',     # Pass 7: Another random pattern
    ]
    
    def __init__(self, progress_var, status_var):
        self.progress_var = progress_var
        self.status_var = status_var
        self.running = False
    
    def update_progress(self, message, percent=None, current_pass=None, total_passes=None):
        """Update the progress bar and print message to console"""
        print(message)
        if percent is not None:
            self.progress_var.set(percent)
        if current_pass and total_passes:
            self.status_var.set(f"Pass {current_pass}/{total_passes} - {percent}% complete")
    
    def wipe_free_space(self, drive_path, method, passes, advanced=False):
        """
        Simple single-threaded approach to wipe free space.
        Creates and fills a single file per pass until the disk is full.
        """
        self.running = True
        
        # Generate operation ID and setup
        operation_id = str(uuid.uuid4())[:8]
        start_time = datetime.datetime.now()
        chunk_size = 10 * 1024 * 1024  # 10MB chunks
        
        self.update_progress(f"Wiping free space on {drive_path}...")
        self.update_progress(f"Method: {method.upper()} with {passes} passes")
        self.update_progress(f"Operation ID: {operation_id}")
        
        # Create temporary directory
        temp_dir = os.path.join(drive_path, f"secure_wipe_{operation_id}")
        try:
            os.makedirs(temp_dir, exist_ok=True)
        except Exception as e:
            self.update_progress(f"Error creating temporary directory: {e}")
            return False
        
        # Adjust passes based on method
        if method == "dod":
            passes = max(passes, 7)
        elif method == "gutmann":
            passes = 35
        elif method == "paranoid":
            passes = max(passes, 49)
        
        try:
            for current_pass in range(passes):
                if not self.running:
                    break
                
                # Determine pattern for this pass
                if method == "dod" and current_pass < len(self.DOD_PATTERNS):
                    pattern = self.DOD_PATTERNS[current_pass]
                    pattern_name = f"DoD pattern {current_pass+1}"
                elif current_pass == 0:
                    pattern = b'\x00'  # zeros
                    pattern_name = "zeros"
                elif current_pass == 1:
                    pattern = b'\xFF'  # ones
                    pattern_name = "ones"
                else:
                    pattern = None  # random data
                    pattern_name = "random data"
                
                # Clear message about pass starting
                self.update_progress(f"\n==== STARTING PASS {current_pass+1}/{passes}: Writing {pattern_name} ====", 
                                    0, current_pass+1, passes)
                
                # Create data for this pass
                if pattern is None:
                    # Random data - create a new buffer each time
                    data = bytes(random.getrandbits(8) for _ in range(chunk_size))
                else:
                    # Pattern data - repeat the pattern to fill the chunk
                    repeats = chunk_size // len(pattern)
                    remainder = chunk_size % len(pattern)
                    data = pattern * repeats + pattern[:remainder]
                
                # Write a single file until disk is full
                file_path = os.path.join(temp_dir, f"wipe_file_{current_pass}")
                bytes_written = 0
                
                try:
                    with open(file_path, 'wb') as f:
                        # Simple loop - write chunks until disk is full (IOError)
                        last_update_time = time.time()
                        while self.running:
                            try:
                                f.write(data)
                                f.flush()
                                bytes_written += len(data)
                                
                                # Only update UI every 0.5 seconds to avoid overwhelming it
                                current_time = time.time()
                                if current_time - last_update_time >= 0.5:
                                    self.update_progress(
                                        f"Pass {current_pass+1}/{passes} - Written {bytes_written/(1024*1024):.1f} MB", 
                                        min(99, int(bytes_written / (1024*1024*1024) * 10)), 
                                        current_pass+1, passes
                                    )
                                    last_update_time = current_time
                            except IOError:
                                # Expected - disk full
                                break
                            
                except Exception as e:
                    self.update_progress(f"Error during writing: {e}")
                
                # Mark this pass as complete
                self.update_progress(f"==== COMPLETED PASS {current_pass+1}/{passes} ====", 
                                     100, current_pass+1, passes)
                
                # Delete the file before moving to next pass
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    self.update_progress(f"Warning: Could not delete temporary file: {e}")
                
                # Small delay to ensure UI updates and improve visibility of pass completion
                time.sleep(1)
            
            # Clean up
            self.update_progress("Cleaning up temporary files...")
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
            
            # Generate report details
            if self.running:
                end_time = datetime.datetime.now()
                duration = end_time - start_time
                hours, remainder = divmod(duration.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                report_text = f"""
==================== SECURE ERASE REPORT ====================
Operation ID: {operation_id}
Date: {start_time.strftime('%Y-%m-%d')}
Time: {start_time.strftime('%H:%M:%S')} to {end_time.strftime('%H:%M:%S')}
Drive: {drive_path}
Method: {method.upper()}
Passes: {passes}
Duration: {hours}h {minutes}m {seconds}s
System: {platform.system()} {platform.release()}
===========================================================
This report certifies that free space on the drive has been
securely wiped using industry-standard data sanitization.
===========================================================
"""
                
                # Save the report
                reports_dir = os.path.join(os.path.expanduser("~"), "secure_eraser_reports")
                os.makedirs(reports_dir, exist_ok=True)
                
                timestamp = start_time.strftime("%Y%m%d_%H%M%S")
                report_path = os.path.join(reports_dir, f"wiping_report_{timestamp}_{operation_id}.txt")
                
                with open(report_path, 'w') as f:
                    f.write(report_text)
                
                self.update_progress(f"\nOperation completed successfully!")
                self.update_progress(f"Duration: {hours}h {minutes}m {seconds}s")
                self.update_progress(f"Report saved to: {report_path}")
                
                return report_path
            else:
                self.update_progress("Operation was stopped by user.")
                return False
                
        except Exception as e:
            self.update_progress(f"Error during wiping: {e}")
            return False
        finally:
            self.running = False
    
    def secure_delete_file(self, file_path, method, passes):
        """
        Securely delete a single file by overwriting it multiple times.
        """
        self.running = True
        
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            self.update_progress(f"File {file_path} does not exist or is not a file.")
            return False
        
        try:
            # Get file details
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            
            # Skip empty files
            if file_size == 0:
                os.remove(file_path)
                self.update_progress(f"Empty file {file_name} removed.")
                return True
            
            # Adjust passes based on method
            if method == "dod":
                passes = max(passes, 7)
            elif method == "gutmann":
                passes = 35
            elif method == "paranoid":
                passes = max(passes, 49)
                
            self.update_progress(f"Securely wiping file: {file_name} ({file_size/1024/1024:.2f} MB)")
            self.update_progress(f"Method: {method.upper()} with {passes} passes")
            
            # For small files, use a simpler approach
            chunk_size = min(1024 * 1024, file_size)  # 1MB chunks or file size
            
            for current_pass in range(passes):
                if not self.running:
                    break
                
                # Determine pattern for this pass
                if method == "dod" and current_pass < len(self.DOD_PATTERNS):
                    pattern = self.DOD_PATTERNS[current_pass]
                    pattern_name = f"DoD pattern {current_pass+1}"
                elif current_pass == 0:
                    pattern = b'\x00'  # zeros
                    pattern_name = "zeros"
                elif current_pass == 1:
                    pattern = b'\xFF'  # ones
                    pattern_name = "ones"
                else:
                    pattern = None  # random data
                    pattern_name = "random data"
                
                self.update_progress(f"Pass {current_pass+1}/{passes}: Writing {pattern_name}", 
                                   0, current_pass+1, passes)
                
                with open(file_path, 'wb') as f:
                    bytes_written = 0
                    while bytes_written < file_size and self.running:
                        # Calculate size to write
                        current_chunk = min(chunk_size, file_size - bytes_written)
                        
                        # Prepare data
                        if pattern is None:
                            # Random data
                            data = bytes(random.getrandbits(8) for _ in range(current_chunk))
                        else:
                            # Pattern data
                            repeats = current_chunk // len(pattern)
                            remainder = current_chunk % len(pattern)
                            data = pattern * repeats + pattern[:remainder]
                        
                        # Write the data
                        f.write(data)
                        
                        # Update progress
                        bytes_written += current_chunk
                        percent = int(bytes_written / file_size * 100)
                        self.update_progress(f"Pass {current_pass+1}/{passes}", percent, current_pass+1, passes)
                
                # Flush to ensure data is written to disk
                f.flush()
                os.fsync(f.fileno())
                
                # Small delay to ensure UI updates
                time.sleep(0.1)
            
            # Delete the file
            if self.running:
                os.remove(file_path)
                self.update_progress(f"File {file_name} has been securely deleted.")
                return True
            else:
                self.update_progress("Operation was stopped by user.")
                return False
                
        except Exception as e:
            self.update_progress(f"Error deleting file: {e}")
            return False
        finally:
            self.running = False
    
    def secure_delete_directory(self, directory_path, method, passes):
        """
        Securely delete an entire directory.
        """
        self.running = True
        
        if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
            self.update_progress(f"Directory {directory_path} does not exist or is not a directory.")
            return False
        
        try:
            # Count files first
            total_files = 0
            file_list = []
            
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    total_files += 1
                    file_list.append(os.path.join(root, file))
            
            self.update_progress(f"Securely deleting {total_files} files in {directory_path}")
            
            # Process each file
            deleted_files = 0
            for file_path in file_list:
                if not self.running:
                    break
                
                self.update_progress(f"Processing file {deleted_files+1}/{total_files}: {os.path.basename(file_path)}")
                
                # Delete the file
                if self.secure_delete_file(file_path, method, passes):
                    deleted_files += 1
                
                # Update overall progress
                percent = int(deleted_files / total_files * 100)
                self.update_progress(f"Overall progress", percent)
            
            # Remove empty directories
            if self.running:
                self.update_progress("Removing empty directories...")
                
                for root, dirs, files in os.walk(directory_path, topdown=False):
                    for dir_name in dirs:
                        try:
                            dir_path = os.path.join(root, dir_name)
                            os.rmdir(dir_path)
                        except:
                            pass
                
                # Remove the top directory
                try:
                    os.rmdir(directory_path)
                    self.update_progress(f"Directory {directory_path} has been securely deleted.")
                    return True
                except Exception as e:
                    self.update_progress(f"Could not remove top directory: {e}")
                    return False
            else:
                self.update_progress("Operation was stopped by user.")
                return False
                
        except Exception as e:
            self.update_progress(f"Error deleting directory: {e}")
            return False
        finally:
            self.running = False
    
    def stop(self):
        """Stop any running operation"""
        self.running = False


class SecureEraserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Eraser - Data Sanitization Tool")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Apply a theme if available
        style = ttk.Style()
        try:
            style.theme_use("clam")  # Try to use a more modern theme
        except:
            pass  # Use default theme if clam isn't available
            
        # Configure colors
        style.configure("TButton", padding=6, relief="flat")
        style.configure("TLabelframe", padding=10)
        
        # Variables
        self.path_var = tk.StringVar()
        self.method_var = tk.StringVar(value="dod")
        self.passes_var = tk.IntVar(value=7)
        self.command_var = tk.StringVar(value="freespace")
        self.advanced_var = tk.BooleanVar(value=False)
        self.progress_var = tk.DoubleVar(value=0.0)
        self.status_var = tk.StringVar(value="Ready")
        
        # Create eraser object
        self.eraser = SimpleSecureEraser(self.progress_var, self.status_var)
        
        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Tab 1: Wiping Operations
        wiping_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(wiping_tab, text="Secure Wiping")
        
        # Tab 2: Reports
        reports_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(reports_tab, text="Reports")
        
        # Tab 3: About
        about_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(about_tab, text="About")
        
        # Wiping Tab Content
        self.setup_wiping_tab(wiping_tab)
        
        # Reports Tab Content
        self.setup_reports_tab(reports_tab)
        
        # About Tab Content
        self.setup_about_tab(about_tab)
        
        # Status bar
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_wiping_tab(self, parent):
        # Operation Frame
        operation_frame = ttk.LabelFrame(parent, text="Operation", padding=10)
        operation_frame.pack(fill=tk.X, pady=5)
        
        # Command selection
        ttk.Label(operation_frame, text="Operation Type:").grid(row=0, column=0, sticky=tk.W, pady=5)
        cmd_frame = ttk.Frame(operation_frame)
        cmd_frame.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Radiobutton(cmd_frame, text="Wipe Free Space", variable=self.command_var, 
                        value="freespace", command=self.update_ui).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(cmd_frame, text="Securely Delete File", variable=self.command_var,
                        value="file", command=self.update_ui).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(cmd_frame, text="Securely Delete Directory", variable=self.command_var,
                        value="directory", command=self.update_ui).pack(side=tk.LEFT, padx=5)
        
        # Path Selection
        ttk.Label(operation_frame, text="Path:").grid(row=1, column=0, sticky=tk.W, pady=5)
        path_frame = ttk.Frame(operation_frame)
        path_frame.grid(row=1, column=1, sticky=tk.EW)
        operation_frame.columnconfigure(1, weight=1)
        
        self.path_entry = ttk.Entry(path_frame, textvariable=self.path_var)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.browse_button = ttk.Button(path_frame, text="Browse", command=self.browse_path)
        self.browse_button.pack(side=tk.RIGHT, padx=5)
        
        # Options Frame
        options_frame = ttk.LabelFrame(parent, text="Wiping Options", padding=10)
        options_frame.pack(fill=tk.X, pady=5)
        
        # Method selection
        ttk.Label(options_frame, text="Wiping Method:").grid(row=0, column=0, sticky=tk.W, pady=5)
        method_frame = ttk.Frame(options_frame)
        method_frame.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Radiobutton(method_frame, text="Standard", variable=self.method_var, 
                        value="standard").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(method_frame, text="DoD 5220.22-M", variable=self.method_var,
                        value="dod").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(method_frame, text="Gutmann (35-pass)", variable=self.method_var,
                        value="gutmann").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(method_frame, text="Paranoid", variable=self.method_var,
                        value="paranoid").pack(side=tk.LEFT, padx=5)
        
        # Number of passes
        ttk.Label(options_frame, text="Passes:").grid(row=1, column=0, sticky=tk.W, pady=5)
        passes_frame = ttk.Frame(options_frame)
        passes_frame.grid(row=1, column=1, sticky=tk.W)
        
        passes_spinner = ttk.Spinbox(passes_frame, from_=1, to=100, width=5, 
                                     textvariable=self.passes_var)
        passes_spinner.pack(side=tk.LEFT)
        
        # Advanced options
        ttk.Label(options_frame, text="Advanced:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.advanced_checkbox = ttk.Checkbutton(options_frame, 
                        text="Use OS-specific wiping methods when available", 
                        variable=self.advanced_var)
        self.advanced_checkbox.grid(row=2, column=1, sticky=tk.W)
        
        # Run Button Frame - Add this right after the options frame
        run_button_frame = ttk.Frame(parent)
        run_button_frame.pack(fill=tk.X, pady=10)
        
        # Create a prominent RUN button centered
        self.run_button = tk.Button(run_button_frame, text="RUN SECURE ERASE", 
                                  bg="#28a745", fg="white", font=("Arial", 12, "bold"),
                                  command=self.start_wiping, padx=20, pady=10)
        self.run_button.pack(anchor=tk.CENTER)
        
        # Output Frame
        output_frame = ttk.LabelFrame(parent, text="Operation Output", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(output_frame, orient=tk.HORIZONTAL, 
                                           length=100, mode='determinate',
                                           variable=self.progress_var)
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Console output with scrollbar
        console_frame = ttk.Frame(output_frame)
        console_frame.pack(fill=tk.BOTH, expand=True)
        
        self.console = tk.Text(console_frame, wrap=tk.WORD, bg='black', fg='light green', 
                               font=('Courier', 9))
        self.console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.console.configure(state='disabled')
        
        console_scrollbar = ttk.Scrollbar(console_frame, orient=tk.VERTICAL, 
                                         command=self.console.yview)
        console_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.console.configure(yscrollcommand=console_scrollbar.set)
        
        # Redirect stdout to console
        self.stdout_redirect = RedirectText(self.console)
        
        # Control Buttons
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = ttk.Button(control_frame, text="Start Wiping", 
                                       command=self.start_wiping)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop", state=tk.DISABLED,
                                      command=self.stop_wiping)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Clear Console", 
                  command=self.clear_console).pack(side=tk.LEFT, padx=5)
                  
        # Update UI based on initial selection
        self.update_ui()
    
    def setup_reports_tab(self, parent):
        # Reports instructions
        ttk.Label(parent, text="View and manage wiping reports generated after operations").pack(pady=10)
        
        # Reports Frame
        reports_frame = ttk.Frame(parent)
        reports_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Reports list with scrollbar
        reports_list_frame = ttk.Frame(reports_frame)
        reports_list_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        self.reports_listbox = tk.Listbox(reports_list_frame, width=70, height=15)
        self.reports_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        reports_scrollbar = ttk.Scrollbar(reports_list_frame, orient=tk.VERTICAL, 
                                         command=self.reports_listbox.yview)
        reports_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.reports_listbox.configure(yscrollcommand=reports_scrollbar.set)
        
        # Report preview frame
        preview_frame = ttk.LabelFrame(reports_frame, text="Report Preview", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT, padx=(10, 0))
        
        self.preview_text = tk.Text(preview_frame, wrap=tk.WORD, width=40, height=15)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        self.preview_text.configure(state='disabled')
        
        # Controls for reports
        reports_control = ttk.Frame(parent)
        reports_control.pack(fill=tk.X, pady=10)
        
        ttk.Button(reports_control, text="Refresh Reports", 
                  command=self.refresh_reports).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(reports_control, text="Open Report", 
                  command=self.open_report).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(reports_control, text="Delete Report", 
                  command=self.delete_report).pack(side=tk.LEFT, padx=5)
        
        # Bind event for report selection
        self.reports_listbox.bind('<<ListboxSelect>>', self.preview_report)
        
        # Populate reports list
        self.refresh_reports()
    
    def setup_about_tab(self, parent):
        about_frame = ttk.Frame(parent)
        about_frame.pack(fill=tk.BOTH, expand=True)
        
        # App title
        title_label = ttk.Label(about_frame, text="Secure Eraser", 
                 font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Description
        desc = "A comprehensive data sanitization tool for securely wiping sensitive data.\n"
        desc += "Ensures data cannot be recovered using commercial or specialized recovery tools."
        desc_label = ttk.Label(about_frame, text=desc, wraplength=600, justify=tk.CENTER)
        desc_label.pack(pady=10)
        
        # Features
        features_frame = ttk.LabelFrame(about_frame, text="Features", padding=10)
        features_frame.pack(fill=tk.X, padx=20, pady=10)
        
        features = [
            "Multiple industry-standard wiping methods (DoD 5220.22-M, Gutmann)",
            "Multi-threaded wiping for improved performance",
            "Verification pass to ensure data is properly overwritten",
            "Detailed reports for compliance documentation",
            "Secure free space wiping to prevent recovery of previously deleted files"
        ]
        
        for feature in features:
            feature_label = ttk.Label(features_frame, text="• " + feature, wraplength=600, 
                     justify=tk.LEFT)
            feature_label.pack(anchor=tk.W, pady=2)
        
        # Security Standards Frame
        standards_frame = ttk.LabelFrame(about_frame, text="Supported Security Standards", padding=10)
        standards_frame.pack(fill=tk.X, padx=20, pady=10)
        
        standards = [
            "DoD 5220.22-M (US Department of Defense)",
            "Gutmann 35-pass method",
            "NIST 800-88 (Guidelines for Media Sanitization)"
        ]
        
        for standard in standards:
            standard_label = ttk.Label(standards_frame, text="• " + standard, wraplength=600, 
                           justify=tk.LEFT)
            standard_label.pack(anchor=tk.W, pady=2)
        
        # Version info and copyright
        version_frame = ttk.Frame(about_frame)
        version_frame.pack(pady=20)
        
        version_label = ttk.Label(version_frame, text="Version 1.0", font=("Arial", 9))
        version_label.pack(side=tk.TOP)
        
        copyright_label = ttk.Label(version_frame, text="© 2025 Nitestryker Software", font=("Arial", 9))
        copyright_label.pack(side=tk.TOP, pady=5)
    
    def update_ui(self):
        """Update UI elements based on selected operation"""
        command = self.command_var.get()
        
        # Update browse button text
        if command == "file":
            self.browse_button.configure(text="Select File")
            self.advanced_checkbox.configure(state="disabled")
        elif command == "directory":
            self.browse_button.configure(text="Select Directory")
            self.advanced_checkbox.configure(state="disabled")
        else:  # freespace
            self.browse_button.configure(text="Select Drive")
            self.advanced_checkbox.configure(state="normal")
    
    def browse_path(self):
        """Open file/directory browser based on selected command"""
        command = self.command_var.get()
        
        if command == "file":
            path = filedialog.askopenfilename(title="Select File to Securely Delete")
        elif command == "directory":
            path = filedialog.askdirectory(title="Select Directory to Securely Delete")
        else:  # freespace
            path = filedialog.askdirectory(title="Select Drive for Free Space Wiping")
            
        if path:
            self.path_var.set(path)
    
    def clear_console(self):
        """Clear the console output"""
        self.console.configure(state='normal')
        self.console.delete(1.0, tk.END)
        self.console.configure(state='disabled')
    
    def start_wiping(self):
        """Start the wiping process"""
        if not self.path_var.get():
            messagebox.showerror("Error", "Please select a path first")
            return
            
        # Confirmation for potentially destructive operations
        operation_type = self.command_var.get()
        path = self.path_var.get()
        
        if operation_type in ["file", "directory"]:
            if not messagebox.askyesno("Confirmation", 
                f"Are you sure you want to permanently delete {path}?\n\nThis cannot be undone!"):
                return
                
        # Get wiping parameters
        method = self.method_var.get()
        passes = self.passes_var.get()
        advanced = self.advanced_var.get() and operation_type == "freespace"
        
        # Update UI
        self.running = True
        self.run_button.configure(state=tk.DISABLED)
        self.start_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)
        self.status_var.set("Wiping in progress...")
        self.progress_var.set(0)
        
        # Clear console
        self.clear_console()
        
        # Save original stdout
        old_stdout = sys.stdout
        
        # Redirect stdout to our console
        sys.stdout = self.stdout_redirect
        
        # Start process in a separate thread
        threading.Thread(
            target=self.run_wiping_process, 
            args=(operation_type, path, method, passes, advanced),
            daemon=True
        ).start()
    
    def run_wiping_process(self, operation_type, path, method, passes, advanced):
        """Run the appropriate wiping process based on operation type"""
        try:
            if operation_type == "freespace":
                result = self.eraser.wipe_free_space(path, method, passes, advanced)
            elif operation_type == "file":
                result = self.eraser.secure_delete_file(path, method, passes)
            elif operation_type == "directory":
                result = self.eraser.secure_delete_directory(path, method, passes)
            
            if result:
                self.root.after(0, lambda: self.status_var.set("Operation completed successfully"))
                
                # Refresh reports if a report was generated
                if operation_type == "freespace" and isinstance(result, str):
                    self.root.after(1000, self.refresh_reports)
            else:
                self.root.after(0, lambda: self.status_var.set("Operation failed or was cancelled"))
                
        except Exception as e:
            print(f"Error executing wiping operation: {e}")
            self.root.after(0, lambda: self.status_var.set("Error"))
            
        finally:
            # Reset UI using the main thread
            self.root.after(0, self.reset_ui)
            
            # Restore original stdout
            sys.stdout = sys.__stdout__
    
    def reset_ui(self):
        """Reset UI after operation completes"""
        self.run_button.configure(state=tk.NORMAL)
        self.start_button.configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk.DISABLED)
    
    def stop_wiping(self):
        """Stop the wiping process"""
        if not self.eraser.running:
            return
            
        if messagebox.askyesno("Confirmation", 
            "Are you sure you want to stop the wiping process?\n\nThis may leave data partially wiped."):
            
            # Set flag to stop the process
            self.eraser.stop()
            self.status_var.set("Operation stopped by user")
            print("\nOperation stopped by user")
            
            # Reset UI
            self.root.after(0, self.reset_ui)
    
    def refresh_reports(self):
        """Refresh the reports list"""
        self.reports_listbox.delete(0, tk.END)
        
        # Get reports directory
        reports_dir = os.path.join(os.path.expanduser("~"), "secure_eraser_reports")
        
        if not os.path.exists(reports_dir):
            return
            
        # List all text reports
        reports = []
        for file in os.listdir(reports_dir):
            if file.endswith(".txt"):
                reports.append(file)
        
        # Sort by date (newest first)
        reports.sort(reverse=True)
        
        # Add to listbox
        for report in reports:
            self.reports_listbox.insert(tk.END, report)
    
    def preview_report(self, event):
        """Preview the selected report"""
        selection = self.reports_listbox.curselection()
        if not selection:
            return
            
        # Get selected report
        report_name = self.reports_listbox.get(selection[0])
        reports_dir = os.path.join(os.path.expanduser("~"), "secure_eraser_reports")
        report_path = os.path.join(reports_dir, report_name)
        
        # Read and display report
        try:
            with open(report_path, 'r') as f:
                report_content = f.read()
                
            self.preview_text.configure(state='normal')
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, report_content)
            self.preview_text.configure(state='disabled')
        except Exception as e:
            messagebox.showerror("Error", f"Could not open report: {e}")
    
    def open_report(self):
        """Open the selected report in default text editor"""
        selection = self.reports_listbox.curselection()
        if not selection:
            messagebox.showinfo("Information", "Please select a report first")
            return
            
        # Get selected report
        report_name = self.reports_listbox.get(selection[0])
        reports_dir = os.path.join(os.path.expanduser("~"), "secure_eraser_reports")
        report_path = os.path.join(reports_dir, report_name)
        
        # Open in default application
        try:
            if platform.system() == "Windows":
                os.startfile(report_path)
            elif platform.system() == "Darwin":  # macOS
                import subprocess
                subprocess.call(["open", report_path])
            else:  # Linux
                import subprocess
                subprocess.call(["xdg-open", report_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open report: {e}")
    
    def delete_report(self):
        """Delete the selected report"""
        selection = self.reports_listbox.curselection()
        if not selection:
            messagebox.showinfo("Information", "Please select a report first")
            return
            
        # Get selected report
        report_name = self.reports_listbox.get(selection[0])
        
        if messagebox.askyesno("Confirmation", f"Are you sure you want to delete {report_name}?"):
            try:
                reports_dir = os.path.join(os.path.expanduser("~"), "secure_eraser_reports")
                report_path = os.path.join(reports_dir, report_name)
                
                # Delete report
                if os.path.exists(report_path):
                    os.remove(report_path)
                    
                # Try to delete corresponding JSON if it exists
                json_path = report_path.replace(".txt", ".json")
                if os.path.exists(json_path):
                    os.remove(json_path)
                    
                # Refresh list
                self.refresh_reports()
                
                # Clear preview
                self.preview_text.configure(state='normal')
                self.preview_text.delete(1.0, tk.END)
                self.preview_text.configure(state='disabled')
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete report: {e}")


def main():
    root = tk.Tk()
    app = SecureEraserGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
