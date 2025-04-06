# Job Management

This guide explains how to use Secure Eraser's job management features to handle long-running operations, including pausing, resuming, and monitoring wiping jobs.

## Understanding Job Management

Secure erasure operations, especially for large volumes of data, can take significant time to complete. Job management allows you to:

1. **Pause and resume** operations
2. **Track progress** of ongoing operations
3. **Cancel** operations if needed
4. **Manage** multiple operations
5. **Recover** from interruptions

## Job Identification

Each wiping operation is assigned a unique job ID that can be used to reference it later:

```bash
python secure_eraser.py --file /path/to/large_file.bin
# Output: Job started with ID: abc123def456
```

You can also specify a custom job ID:

```bash
python secure_eraser.py --file /path/to/large_file.bin --job-id my_custom_job
```

## Listing Available Jobs

To see all currently available jobs:

```bash
python secure_eraser.py --list-jobs
```

This displays:
- Job ID
- Status (running, paused, completed, failed)
- Target (file, directory, drive)
- Progress
- Start time
- Estimated completion time

## Resuming a Paused Job

To resume a previously paused job:

```bash
python secure_eraser.py --job-id abc123def456
```

This continues the operation from where it left off.

## Pausing a Running Job

To pause a running job:

```bash
# Using keyboard interrupt
# Press Ctrl+C during operation

# Using job ID
python secure_eraser.py --pause-job abc123def456
```

## Canceling a Job

To cancel a job permanently:

```bash
python secure_eraser.py --cancel-job abc123def456
```

This terminates the operation and cannot be resumed.

## Deleting a Job

To remove a completed or failed job from the job list:

```bash
python secure_eraser.py --delete-job abc123def456
```

This removes the job metadata but does not affect the target files.

## Monitoring Job Progress

### Viewing Job Details

To see detailed information about a specific job:

```bash
python secure_eraser.py --job-details abc123def456
```

This shows comprehensive information including:
- Current progress
- Time elapsed
- Time remaining
- Performance metrics
- Error logs (if any)

### Real-time Monitoring

To monitor a job in real-time:

```bash
python secure_eraser.py --monitor-job abc123def456
```

This displays a live updating view of the job progress.

## Advanced Job Management

### Setting Job Priority

You can set priority levels for jobs:

```bash
python secure_eraser.py --file /path/to/file.txt --job-priority high
```

Priorities include: low, normal, high, critical

### Job Dependencies

You can create job chains where one job starts after another completes:

```bash
python secure_eraser.py --file /path/to/file1.txt --job-id job1
python secure_eraser.py --file /path/to/file2.txt --after-job job1
```

### Job Scheduling

Schedule jobs to run at specific times:

```bash
python secure_eraser.py --file /path/to/file.txt --schedule "2025-04-10 22:00"
```

This creates a job that will start at the specified time.

## Automatic Recovery

Secure Eraser automatically saves job state periodically, allowing recovery from unexpected interruptions:

```bash
# If the program crashes or the system shuts down unexpectedly
# Simply restart with the job ID
python secure_eraser.py --job-id abc123def456
```

## Job Notifications

Receive notifications about job status:

```bash
python secure_eraser.py --file /path/to/file.txt --notify-on-completion --email user@example.com
```

Available notification options:
- `--notify-on-completion`: Send notification when job completes
- `--notify-on-error`: Send notification if job encounters errors
- `--notify-on-pause`: Send notification if job is paused

## Job Reporting

Generate detailed reports for jobs:

```bash
python secure_eraser.py --job-report abc123def456 --report-format html --report-path job_report.html
```

This creates a comprehensive report of the job, including:
- Operation details
- Time statistics
- Progress information
- Verification results (if applicable)

## Job Configuration Files

For complex job configurations, you can use a configuration file:

```bash
python secure_eraser.py --job-config /path/to/job_config.json
```

Example job configuration file:
```json
{
  "target": {
    "type": "file",
    "path": "/path/to/file.txt"
  },
  "method": "dod_7pass",
  "verify": true,
  "job_id": "custom_job_123",
  "priority": "high",
  "reporting": {
    "format": "html",
    "path": "/path/to/reports/job_report.html",
    "sign": true
  },
  "performance": {
    "workers": 4,
    "gpu": true,
    "optimize_resources": true
  },
  "notifications": {
    "on_completion": true,
    "email": "user@example.com"
  }
}
```

## Best Practices

1. **Use descriptive job IDs** for easier management
2. **Monitor system resources** during long-running jobs
3. **Set appropriate priorities** based on urgency
4. **Schedule resource-intensive jobs** during off-peak hours
5. **Use notifications** for long-running operations
6. **Generate reports** for completed jobs
7. **Regularly clean up** old job metadata

## Troubleshooting

### Job Won't Resume

If a job won't resume:
- Check if the target file/directory still exists
- Verify permissions
- Check for locks on the target
- Examine job logs for errors

### Job Slow or Stalled

If a job is performing poorly:
- Check system resources
- Consider adjusting performance parameters
- Verify there are no disk issues
- Try pausing and resuming the job

### Job Database Corruption

If the job database becomes corrupted:
- Use the recovery tool:
  ```bash
  python secure_eraser.py --repair-job-database
  ```
- If repair fails, you may need to reset:
  ```bash
  python secure_eraser.py --reset-job-database
  ```
  (This will lose all job history)

## Related Documentation

- [Performance Optimization](performance.md) - Optimizing job performance
- [Reporting](reporting.md) - Detailed job reports
- [Troubleshooting](troubleshooting.md) - General troubleshooting guide