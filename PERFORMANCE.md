# Performance Optimizations

The Secure Eraser tool includes several performance optimization features to improve efficiency and throughput, especially for large files and batch operations.

## Batch Processing

The batch processing feature allows you to efficiently process multiple files and directories in a single command. This is particularly useful for securely erasing large sets of files.

```bash
# Process multiple files from a batch file
python secure_eraser.py --batch file_list.txt
```

Where `file_list.txt` contains a list of file or directory paths to process, one per line:

```
/path/to/file1.txt
/path/to/file2.bin
/path/to/sensitive_directory
```

You can also specify the number of worker threads:

```bash
# Process with 4 parallel workers
python secure_eraser.py --batch file_list.txt --workers 4
```

## GPU Acceleration

For systems with compatible NVIDIA GPUs and CUDA support, Secure Eraser can leverage GPU acceleration to speed up data generation for wiping operations:

```bash
# Enable GPU acceleration
python secure_eraser.py --file large_file.bin --gpu
```

The GPU acceleration:
- Automatically detects available CUDA-capable devices
- Offloads secure data generation to the GPU
- Falls back to CPU processing if no GPU is available or if an error occurs
- Can provide significant performance improvements for very large files

## Resource Optimization

The resource optimizer dynamically adjusts parameters based on your system's capabilities and current load:

```bash
# Enable automatic resource optimization
python secure_eraser.py --file large_file.bin --optimize-resources
```

This feature:
- Adjusts chunk sizes based on available memory
- Optimizes thread count based on CPU availability and load
- Sets I/O priorities based on system I/O pressure
- Prevents system overload during long operations

You can also manually specify chunk size (in MB):

```bash
# Set specific chunk size
python secure_eraser.py --file large_file.bin --chunk-size 50
```

## Pause/Resume Capability

Long-running wiping operations can be paused and resumed, which is especially useful for very large files or drives:

```bash
# Start an operation (Ctrl+C to pause)
python secure_eraser.py --drive /path/to/drive --force

# Resume a paused operation
python secure_eraser.py --job-id abc123def456
```

Job management operations:
```bash
# List all available jobs
python secure_eraser.py --list-jobs

# Cancel a job
python secure_eraser.py --cancel-job abc123def456

# Delete a completed job
python secure_eraser.py --delete-job abc123def456
```

## Performance Tips

1. For large files, use `--optimize-resources` to automatically optimize parameters
2. For many small files, increase worker count: `--workers 8`
3. For very large drives, enable GPU acceleration: `--gpu`
4. Use the standard method with fewer passes for faster operation when high security isn't required
5. Run with `--verbose` to see real-time performance data
6. On systems with limited RAM, set a smaller chunk size: `--chunk-size 10`
7. For the highest performance on multi-core systems, use a combination of options:
   ```bash
   python secure_eraser.py --batch file_list.txt --gpu --optimize-resources --workers 8
   ```

## System Requirements

- GPU Acceleration: CUDA-capable NVIDIA GPU with compute capability 2.0+
- Batch Processing: Recommended minimum 4GB RAM, scales with file sizes
- Resource Optimization: Works on all systems, but provides more benefit on systems with 4+ CPU cores