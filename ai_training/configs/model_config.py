from typing import Dict, Any
import os

# Base configuration for AI models
AI_MODEL_CONFIG: Dict[str, Any] = {
    'montage_analysis': {
        'model_type': 'transformer',
        'input_size': (224, 224),
        'sequence_length': 32,
        'learning_rate': 0.001,
        'batch_size': 16,
        'epochs': 100
    },
    'style_transfer': {
        'model_type': 'gan',
        'content_weight': 1.0,
        'style_weight': 100.0,
        'learning_rate': 0.0001,
        'batch_size': 4,
        'epochs': 50
    },
    'effect_generation': {
        'model_type': 'autoencoder',
        'latent_dim': 128,
        'learning_rate': 0.001,
        'batch_size': 32,
        'epochs': 75
    }
}

# Create necessary directories
def create_training_directories():
    """Create the directory structure for AI training data."""
    directories = [
        'montage_data/raw',
        'montage_data/processed',
        'montage_data/annotations',
        'art_packs/overlays',
        'art_packs/effects',
        'art_packs/styles',
        'configs'
    ]
    
    for directory in directories:
        os.makedirs(os.path.join('ai_training', directory), exist_ok=True)

if __name__ == '__main__':
    create_training_directories()
