"""
Utility functions for the Cours Organizer application.
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import hashlib
import uuid


def generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())


def generate_hash(text: str) -> str:
    """Generate a hash for text."""
    return hashlib.md5(text.encode()).hexdigest()


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for safe storage."""
    # Remove special characters
    filename = re.sub(r'[^\w\s.-]', '_', filename)
    # Remove leading/trailing whitespace
    filename = filename.strip()
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    return filename


def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    return Path(filename).suffix.lower()


def get_file_type(filename: str) -> str:
    """Get file type category."""
    ext = get_file_extension(filename).lower()
    
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif', '.webp']
    document_extensions = ['.pdf', '.docx', '.doc', '.txt', '.md', '.markdown']
    
    if ext in image_extensions:
        return "image"
    elif ext in document_extensions:
        return "document"
    else:
        return "unknown"


def format_date(date: datetime) -> str:
    """Format date for display."""
    return date.strftime("%Y-%m-%d %H:%M:%S")


def format_date_french(date: datetime) -> str:
    """Format date in French format."""
    return date.strftime("%d/%m/%Y %H:%M:%S")


def time_ago(date: datetime) -> str:
    """Calculate time ago from date."""
    now = datetime.utcnow()
    delta = now - date
    
    if delta.days > 365:
        years = delta.days // 365
        return f"il y a {years} an{'s' if years > 1 else ''}"
    elif delta.days > 30:
        months = delta.days // 30
        return f"il y a {months} mois"
    elif delta.days > 0:
        return f"il y a {delta.days} jour{'s' if delta.days > 1 else ''}"
    elif delta.seconds > 3600:
        hours = delta.seconds // 3600
        return f"il y a {hours} heure{'s' if hours > 1 else ''}"
    elif delta.seconds > 60:
        minutes = delta.seconds // 60
        return f"il y a {minutes} minute{'s' if minutes > 1 else ''}"
    else:
        return "à l'instant"


def read_json_file(file_path: str) -> Optional[Dict]:
    """Read a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None


def write_json_file(file_path: str, data: Dict) -> bool:
    """Write data to a JSON file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except:
        return False


def ensure_directory_exists(directory: str) -> bool:
    """Ensure a directory exists, create if not."""
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except:
        return False


def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    try:
        return os.path.getsize(file_path)
    except:
        return 0


def get_file_size_human(file_path: str) -> str:
    """Get human-readable file size."""
    size = get_file_size(file_path)
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"


def split_text_into_chunks(text: str, chunk_size: int = 1000) -> List[str]:
    """Split text into chunks of specified size."""
    chunks = []
    words = text.split()
    
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= chunk_size:
            current_chunk.append(word)
            current_length += len(word) + 1
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word) + 1
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks


def clean_text(text: str) -> str:
    """Clean text by removing excessive whitespace and special characters."""
    if not text:
        return ""
    
    # Replace multiple newlines with single newline
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Replace multiple spaces with single space
    text = re.sub(r'[ \t]{2,}', ' ', text)
    
    # Trim whitespace
    text = text.strip()
    
    return text


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to maximum length."""
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length]
    if len(text) > max_length:
        truncated += "..."
    
    return truncated


def get_config() -> Dict:
    """Get application configuration."""
    config = {
        "app_name": "Cours Organizer",
        "version": "1.0.0",
        "debug": os.getenv("DEBUG", "false").lower() == "true",
        "database_url": os.getenv("DATABASE_URL", "sqlite:///./cours_organizer.db"),
        "upload_dir": os.getenv("UPLOAD_DIR", "uploads"),
        "processed_dir": os.getenv("PROCESSED_DIR", "processed"),
        "anki_host": os.getenv("ANKI_HOST", "localhost"),
        "anki_port": int(os.getenv("ANKI_PORT", "8765")),
        "ocr_language": os.getenv("OCR_LANGUAGE", "fra+eng"),
    }
    
    return config


def get_mime_type(file_path: str) -> str:
    """Get MIME type for a file."""
    ext = get_file_extension(file_path).lower()
    
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.tiff': 'image/tiff',
        '.pdf': 'application/pdf',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.doc': 'application/msword',
        '.txt': 'text/plain',
        '.md': 'text/markdown',
    }
    
    return mime_types.get(ext, 'application/octet-stream')
