# Installation Guide

This guide explains how to install and set up Secure Eraser on different operating systems.

## System Requirements

Before installing Secure Eraser, ensure your system meets these minimum requirements:

### Hardware Requirements
- **CPU**: Any modern multi-core processor (2+ cores recommended)
- **RAM**: 2GB minimum, 4GB+ recommended for large files
- **Disk Space**: 100MB for installation
- **Optional GPU**: NVIDIA GPU with CUDA support for GPU acceleration

### Operating System Requirements
- **Linux**: Any modern distribution (Ubuntu 20.04+, Debian 10+, CentOS 8+, etc.)
- **macOS**: macOS 10.15 (Catalina) or later
- **Windows**: Windows 10 or later

### Software Requirements
- **Python**: Python 3.9 or higher
- **Package Manager**: pip (usually included with Python)

## Basic Installation

### Installing from PyPI (Recommended)

The easiest way to install Secure Eraser is from PyPI:

```bash
pip install secure-eraser
```

This installs the latest stable version with basic dependencies.

### Installing from Source

For the latest development version:

```bash
# Clone the repository
git clone https://github.com/username/secure-eraser.git
cd secure-eraser

# Install the package
pip install .
```

## Advanced Installation

### Installing with All Features

To install Secure Eraser with all optional dependencies:

```bash
pip install secure-eraser[full]
```

This includes:
- GPU acceleration support
- PDF reporting
- HTML reports with visualizations
- Digital signing
- Advanced memory protection

### Installing Specific Feature Sets

Install only the dependencies you need:

```bash
# For GPU acceleration
pip install secure-eraser[gpu]

# For reporting features
pip install secure-eraser[reports]

# For enhanced security features
pip install secure-eraser[security]
```

## Platform-Specific Instructions

### Linux Installation

#### Ubuntu/Debian

```bash
# Install Python and dependencies
sudo apt update
sudo apt install python3 python3-pip python3-dev

# Install Secure Eraser
pip3 install secure-eraser
```

#### RedHat/CentOS/Fedora

```bash
# Install Python and dependencies
sudo dnf install python3 python3-pip python3-devel

# Install Secure Eraser
pip3 install secure-eraser
```

#### GPU Support on Linux

For GPU acceleration on Linux:

```bash
# Install CUDA toolkit (example for Ubuntu)
sudo apt install nvidia-cuda-toolkit

# Install PyCUDA and Secure Eraser with GPU support
pip3 install pycuda
pip3 install secure-eraser[gpu]
```

### macOS Installation

Using Homebrew:

```bash
# Install Python
brew install python3

# Install Secure Eraser
pip3 install secure-eraser
```

### Windows Installation

1. Download and install Python 3.9+ from [python.org](https://www.python.org/downloads/)
2. Ensure you check "Add Python to PATH" during installation
3. Open Command Prompt as administrator and run:

```batch
pip install secure-eraser
```

#### GPU Support on Windows

For GPU acceleration on Windows:

1. Download and install the NVIDIA CUDA Toolkit from [NVIDIA's website](https://developer.nvidia.com/cuda-downloads)
2. Install GPU dependencies:

```batch
pip install pycuda
pip install secure-eraser[gpu]
```

## Docker Installation

Secure Eraser can be run in a Docker container:

```bash
# Pull the Docker image
docker pull username/secure-eraser:latest

# Run Secure Eraser in a container
docker run -v /path/to/data:/data username/secure-eraser --file /data/file.txt
```

## Virtual Environment Installation (Recommended)

Using a virtual environment is recommended to avoid dependency conflicts:

```bash
# Create a virtual environment
python -m venv secure-eraser-env

# Activate the environment
# On Linux/macOS:
source secure-eraser-env/bin/activate
# On Windows:
secure-eraser-env\Scripts\activate

# Install Secure Eraser
pip install secure-eraser

# When finished, deactivate the environment
deactivate
```

## Post-Installation Verification

Verify your installation:

```bash
# Check the installed version
secure-eraser --version

# Run a basic test
secure-eraser --test
```

## Common Installation Issues

### Missing Dependencies

If you encounter missing dependency errors:

```bash
pip install -r requirements.txt
```

### Permission Issues

If you encounter permission errors on Linux/macOS:

```bash
pip install --user secure-eraser
```

On Windows, run Command Prompt as administrator.

### CUDA Installation Issues

If GPU acceleration doesn't work:

1. Verify NVIDIA drivers are installed:
   ```bash
   nvidia-smi
   ```

2. Verify CUDA installation:
   ```bash
   nvcc --version
   ```

3. Reinstall PyCUDA:
   ```bash
   pip uninstall pycuda
   pip install pycuda
   ```

## Upgrading Secure Eraser

To upgrade to the latest version:

```bash
pip install --upgrade secure-eraser
```

## Uninstalling

To remove Secure Eraser:

```bash
pip uninstall secure-eraser
```

## Developer Installation

For developers who want to contribute:

```bash
# Clone the repository
git clone https://github.com/username/secure-eraser.git
cd secure-eraser

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

## System-Wide Installation

For system-wide installation (requires admin/root):

```bash
# Linux/macOS
sudo pip install secure-eraser

# Windows (run Command Prompt as Administrator)
pip install secure-eraser
```

## Configuration

### Default Configuration

After installation, you can create a default configuration:

```bash
secure-eraser --create-config
```

This creates a configuration file at:
- Linux/macOS: `~/.config/secure-eraser/config.json`
- Windows: `%APPDATA%\secure-eraser\config.json`

### Custom Configuration Location

To use a custom configuration file:

```bash
secure-eraser --config /path/to/custom-config.json
```

## Next Steps

After installation:

1. Review the [Basic Usage](basic_usage.md) guide
2. Check the [Security Standards](security_standards.md) documentation
3. Explore [Performance Options](performance.md) for your system

## Related Documentation

- [Basic Usage](basic_usage.md) - Getting started with Secure Eraser
- [Troubleshooting](troubleshooting.md) - Solutions to common problems
- [Development](development.md) - Contributing to Secure Eraser