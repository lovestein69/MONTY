import os
import logging
from typing import List
from werkzeug.utils import secure_filename
from config import ALLOWED_EXTENSIONS

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def allowed_file(filename: str) -> bool:
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clean_directory(directory: str) -> None:
    """Remove all files from specified directory."""
    try:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        logger.debug(f"Cleaned directory: {directory}")
    except Exception as e:
        logger.error(f"Error cleaning directory {directory}: {str(e)}")
        raise

def save_uploaded_file(file, directory: str, filename: str = None) -> str:
    """Save uploaded file to specified directory with secure filename."""
    if not file:
        raise ValueError("No file provided")
    
    secure_name = secure_filename(filename or file.filename)
    file_path = os.path.join(directory, secure_name)
    
    try:
        file.save(file_path)
        logger.debug(f"Saved file: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error saving file {file_path}: {str(e)}")
        raise

def validate_clips(clips: List) -> bool:
    """Validate number of clips and their formats."""
    if not (3 <= len(clips) <= 6):
        return False
    return all(allowed_file(clip.filename) for clip in clips if clip)
