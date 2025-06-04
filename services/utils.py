from datetime import datetime
from typing import Dict, Any


def format_file_size(size_bytes: int) -> str:
    """Convert bytes to human readable format"""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"


def format_file_info(file_info: Dict[str, Any]) -> Dict[str, Any]:
    """Format file information for display"""
    if not file_info:
        return {}

    return {
        "ContentLength": format_file_size(file_info["ContentLength"]),
        "ContentType": file_info.get("ContentType", "Unknown"),
        "LastModified": file_info["LastModified"].strftime("%Y-%m-%d %H:%M:%S"),
        "ETag": file_info["ETag"].strip('"'),
        "StorageClass": file_info.get("StorageClass", "STANDARD"),
    }
