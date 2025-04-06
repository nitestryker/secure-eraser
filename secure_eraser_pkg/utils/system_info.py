"""
System information utilities for the Secure Eraser tool.
"""

import platform
import os
import socket
import psutil
import datetime
import logging
from typing import Dict, Any, Optional

# Try to import optional CPU info package
try:
    import py_cpuinfo as cpuinfo
    CPUINFO_AVAILABLE = True
except ImportError:
    CPUINFO_AVAILABLE = False


def get_system_info() -> Dict[str, Any]:
    """
    Get detailed system information.
    
    Returns:
        Dictionary containing system information
    """
    try:
        system_info = {
            "timestamp": datetime.datetime.now().isoformat(),
            "hostname": socket.gethostname(),
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "cpu_info": get_cpu_info(),
            "memory_total": get_memory_info()["total_gb"],
            "memory_available": get_memory_info()["available_gb"],
            "disk_info": get_disk_info()
        }
        return system_info
    except Exception as e:
        logging.error(f"Error getting system info: {e}")
        return {"error": str(e)}


def get_cpu_info() -> Dict[str, Any]:
    """
    Get CPU information.
    
    Returns:
        Dictionary containing CPU information
    """
    cpu_info = {
        "count": psutil.cpu_count(logical=True),
        "physical_count": psutil.cpu_count(logical=False) or 1,
        "percent": psutil.cpu_percent(interval=0.1),
    }
    
    # Try to get detailed CPU info if py-cpuinfo is available
    if CPUINFO_AVAILABLE:
        try:
            info = cpuinfo.get_cpu_info()
            cpu_info["brand"] = info.get("brand_raw", "Unknown")
            cpu_info["hz"] = info.get("hz_advertised_friendly", "Unknown")
            cpu_info["arch"] = info.get("arch", "Unknown")
            cpu_info["bits"] = info.get("bits", 64)
        except Exception:
            cpu_info["brand"] = platform.processor() or "Unknown"
    else:
        cpu_info["brand"] = platform.processor() or "Unknown"
    
    return cpu_info


def get_memory_info() -> Dict[str, Any]:
    """
    Get memory information.
    
    Returns:
        Dictionary containing memory information
    """
    mem = psutil.virtual_memory()
    return {
        "total": mem.total,
        "available": mem.available,
        "percent": mem.percent,
        "used": mem.used,
        "free": mem.free,
        "total_gb": mem.total / (1024**3),
        "available_gb": mem.available / (1024**3),
        "used_gb": mem.used / (1024**3)
    }


def get_disk_info() -> Dict[str, Dict[str, Any]]:
    """
    Get disk information.
    
    Returns:
        Dictionary mapping mount points to disk information
    """
    disks = {}
    
    for part in psutil.disk_partitions(all=False):
        if os.name == 'nt' and ('cdrom' in part.opts or part.fstype == ''):
            # Skip CD-ROM drives on Windows
            continue
            
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks[part.mountpoint] = {
                "device": part.device,
                "fstype": part.fstype,
                "opts": part.opts,
                "total": usage.total / (1024**3),  # GB
                "used": usage.used / (1024**3),    # GB
                "free": usage.free / (1024**3),    # GB
                "percent": usage.percent
            }
        except PermissionError:
            # Some mountpoints require root permissions
            continue
    
    return disks