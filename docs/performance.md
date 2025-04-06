# Performance Optimization

This guide explains the performance optimization features of Secure Eraser, which enable efficient processing of large volumes of data.

## Performance Features Overview

Secure Eraser includes several performance optimizations:

1. **Multi-threaded Processing**: Parallel execution using multiple CPU cores
2. **GPU Acceleration**: Utilizing graphics hardware for faster processing
3. **Resource Optimization**: Dynamic adjustment based on system load
4. **Chunked Processing**: Memory-efficient handling of large files
5. **Batch Processing**: Efficient processing of multiple files

## Multi-threaded Processing

Enable multi-threaded processing by specifying the number of worker threads:

```bash
python secure_eraser.py --file /path/to/file.txt --workers 4
```

This uses 4 worker threads to process the file in parallel.

### Automatic Worker Count

If you don't specify the number of workers, Secure Eraser will automatically determine the optimal number based on your system's CPU:

```bash
python secure_eraser.py --file /path/to/file.txt --workers auto
```

This is the default setting if `--workers` is not specified.

### Worker Count Recommendations

- For general use: Use `auto` or set to the number of physical CPU cores
- For maximum performance: Set to the number of logical CPU cores
- For background processing: Set to half the number of cores
- For critical systems: Limit to specific number to prevent resource exhaustion

## GPU Acceleration

For systems with compatible graphics hardware, enable GPU acceleration:

```bash
python secure_eraser.py --file /path/to/large_file.bin --gpu
```

GPU acceleration is particularly effective for:
- Large files (100MB+)
- Operations with simple patterns
- Systems with CUDA-compatible NVIDIA GPUs

### GPU Acceleration Requirements

- CUDA-compatible NVIDIA GPU
- PyCUDA and CUDA Toolkit installed
- Sufficient GPU memory for the operation

### Combining GPU with Workers

For optimal performance on systems with both multi-core CPUs and GPUs:

```bash
python secure_eraser.py --file /path/to/large_file.bin --gpu --workers 4
```

This uses both GPU acceleration and multi-threading.

## Resource Optimization

Enable dynamic resource optimization:

```bash
python secure_eraser.py --file /path/to/file.txt --optimize-resources
```

This feature:
- Adjusts CPU and I/O priority based on system load
- Monitors and adapts to available memory
- Throttles processing to prevent system overload
- Adjusts chunk sizes dynamically

### Resource Optimization Use Cases

- **Server environments**: Preventing impact on other services
- **Shared systems**: Being considerate of other users
- **Long-running operations**: Adapting to changing system conditions
- **Critical systems**: Ensuring system stability during wiping

## Chunked Processing

Specify custom chunk sizes for memory-efficient processing:

```bash
python secure_eraser.py --file /path/to/huge_file.bin --chunk-size 50
```

This processes the file in 50MB chunks, reducing memory usage.

### Chunk Size Recommendations

- For regular files: The default automatic sizing works well
- For very large files: 10-50MB chunks balance memory usage and performance
- For systems with limited RAM: Use smaller chunks (5-10MB)
- For high-performance systems: Larger chunks (100MB+) may improve throughput

## Batch Processing

Process multiple files efficiently using batch mode:

```bash
python secure_eraser.py --batch file_list.txt
```

Where `file_list.txt` contains file paths, one per line.

### Advanced Batch Processing

Combine batch processing with other performance features:

```bash
python secure_eraser.py --batch file_list.txt --gpu --workers 8 --optimize-resources
```

## Performance Monitoring

View performance metrics during execution with verbose mode:

```bash
python secure_eraser.py --file /path/to/file.txt --verbose
```

This shows real-time throughput, resource usage, and estimated completion time.

## Performance for Different Media Types

### HDD Optimization

For traditional hard drives:

```bash
python secure_eraser.py --file /path/to/file.txt --optimize-for hdd
```

This optimizes for sequential access patterns typical of HDDs.

### SSD Optimization

For solid-state drives:

```bash
python secure_eraser.py --file /path/to/file.txt --optimize-for ssd
```

This optimizes for the parallel nature and wear-leveling characteristics of SSDs.

## Advanced Performance Techniques

### Pipeline Processing

For complex operations, enable pipeline mode:

```bash
python secure_eraser.py --file /path/to/file.txt --pipeline-mode
```

This creates a processing pipeline where reading, wiping, and verification happen simultaneously on different portions of the data.

### Adaptive Pass Scheduling

For methods with multiple passes, optimize pass scheduling:

```bash
python secure_eraser.py --file /path/to/file.txt --method gutmann --adaptive-passes
```

This intelligently schedules different passes to maximize I/O efficiency.

## Performance Best Practices

1. **Start with defaults**: Let Secure Eraser auto-configure for your system
2. **Enable GPU for large files**: If you have a compatible GPU
3. **Adjust worker count for background tasks**: Reduce workers for background operations
4. **Use batch processing for multiple files**: Rather than sequential individual operations
5. **Enable resource optimization for shared systems**: To be a good neighbor
6. **Monitor performance with verbose mode**: To identify bottlenecks

## Performance Troubleshooting

### High CPU Usage

If CPU usage is too high:
- Reduce worker count
- Enable `--optimize-resources`
- Use `--nice` to lower process priority

```bash
python secure_eraser.py --file /path/to/file.txt --workers 2 --optimize-resources --nice 10
```

### High Memory Usage

If memory usage is too high:
- Reduce chunk size
- Disable GPU acceleration
- Use streaming mode

```bash
python secure_eraser.py --file /path/to/file.txt --chunk-size 10 --streaming-mode
```

### Slow Performance

If performance is slower than expected:
- Try enabling GPU acceleration
- Increase worker count
- Optimize for the specific storage type
- Use a simpler wiping method if security requirements allow

### GPU Errors

If GPU acceleration causes errors:
- Ensure GPU drivers are up to date
- Reduce GPU memory usage
- Fall back to CPU-only mode

## Related Documentation

- [Basic Usage](basic_usage.md) - Fundamental operations
- [Job Management](job_management.md) - Managing long-running operations
- [Troubleshooting](troubleshooting.md) - General troubleshooting guide