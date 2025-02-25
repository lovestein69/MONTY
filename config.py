import os
from typing import Dict, Any

# Video settings
CLIP_DURATION: float = 69.0  # Total duration in seconds
MAIN_BODY_DURATION: float = 60.0  # Main content duration
TRANSITION_DURATION: float = 0.5  # Crossfade duration
INTRO_DURATION: float = 4.5
OUTRO_DURATION: float = 4.5

# Filter configurations
FILTERS: Dict[str, Dict[str, Any]] = {
    'warm': {
        'enabled': True,
        'intensity': 0.4,
        'description': 'Warm orange/red tint filter'
    },
    'cool': {
        'enabled': True,
        'intensity': 0.4,
        'description': 'Cool blue tint filter'
    },
    'cinematic': {
        'enabled': True,
        'contrast': 1.2,
        'saturation': 0.85,
        'description': 'Movie-like color grading filter'
    }
}

# File settings
UPLOAD_FOLDER = 'uploads'
CLIPS_FOLDER = 'clips'
ASSETS_FOLDER = 'assets'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mp3'}

# Create required directories
for folder in [UPLOAD_FOLDER, CLIPS_FOLDER, ASSETS_FOLDER]:
    os.makedirs(folder, exist_ok=True)
