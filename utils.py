import os
from typing import Set, List

def allowed_file(filename: str, allowed_extensions: Set[str]) -> bool:
    """Check if a filename has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def ensure_directories_exist(directories: List[str]) -> None:
    """Ensure all required directories exist"""
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def clear_directory(directory: str) -> None:
    """Remove all files in a directory"""
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error: {e}")