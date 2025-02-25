import os
from typing import Dict, Any

# Video settings
CLIP_DURATION: float = 69.0  # Total duration in seconds
MAIN_BODY_DURATION: float = 60.0  # Main content duration
TRANSITION_DURATION: float = 0.5  # Crossfade duration
INTRO_DURATION: float = 4.5
OUTRO_DURATION: float = 4.5

# Art Pack configurations
ART_PACKS: Dict[str, Dict[str, Any]] = {
    'classic': {
        'name': 'Classic',
        'description': 'Standard color grading with subtle enhancements',
        'filters': ['warm', 'cool', 'cinematic']
    },
    'vintage': {
        'name': 'Vintage',
        'description': 'Retro look with warm tones and film grain',
        'filters': ['sepia', 'grain', 'vignette']
    },
    'neon': {
        'name': 'Neon',
        'description': 'Vibrant colors with high contrast',
        'filters': ['vibrant', 'glow', 'contrast']
    },
    'minimal': {
        'name': 'Minimal',
        'description': 'Clean and simple look with subtle gradients',
        'filters': ['clean', 'soft', 'gradient']
    }
}

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
    },
    'sepia': {
        'enabled': True,
        'intensity': 0.5,
        'description': 'Vintage sepia tone effect'
    },
    'grain': {
        'enabled': True,
        'amount': 0.3,
        'description': 'Film grain effect'
    },
    'vignette': {
        'enabled': True,
        'amount': 0.4,
        'description': 'Dark corners vignette effect'
    },
    'vibrant': {
        'enabled': True,
        'saturation': 1.4,
        'description': 'Enhanced color vibrancy'
    },
    'glow': {
        'enabled': True,
        'radius': 10,
        'intensity': 0.3,
        'description': 'Soft glow effect'
    },
    'contrast': {
        'enabled': True,
        'amount': 1.3,
        'description': 'Enhanced contrast'
    },
    'clean': {
        'enabled': True,
        'sharpness': 1.1,
        'description': 'Clean, sharp look'
    },
    'soft': {
        'enabled': True,
        'blur': 0.2,
        'description': 'Soft, dreamy effect'
    },
    'gradient': {
        'enabled': True,
        'colors': [(255,200,100), (100,150,255)],
        'description': 'Subtle color gradient overlay'
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