from typing import Dict, Any

# Configuration settings
CLIP_DURATION: int = 69  # Total duration in seconds
MAIN_BODY_DURATION: int = 60  # Main content duration
TRANSITION_DURATION: float = 0.5  # Crossfade duration
INTRO_DURATION: float = 4.5
OUTRO_DURATION: float = 4.5

# Upload settings
UPLOAD_FOLDER: str = 'uploads'
MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS: set = {'mp4', 'avi', 'mov', 'mp3'}

# Directory paths
CLIPS_DIR: str = 'clips'
ASSETS_DIR: str = 'assets'

# Filter settings
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
