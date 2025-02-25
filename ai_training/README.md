# MONTY AI Training Data

This directory contains the training data and configuration for MONTY's AI models.

## Directory Structure

```
ai_training/
├── montage_data/       # Gaming montage training data
│   ├── raw/           # Raw video clips
│   ├── processed/     # Preprocessed video data
│   └── annotations/   # Video annotations and metadata
├── art_packs/         # Art pack training data
│   ├── overlays/      # Visual overlay assets
│   ├── effects/       # Effect templates
│   └── styles/        # Style transfer models
└── configs/           # Training configurations
```

## Data Organization

### Montage Data
- Place gaming montage clips in `montage_data/raw/`
- Each clip should be labeled with game type and key moments
- Annotations should include timing of key events

### Art Packs
- Place art assets in appropriate subdirectories under `art_packs/`
- Each art pack should have its own configuration in `configs/`
- Include reference images and style templates

## Model Training

The AI models will be trained to:
1. Analyze gaming montages for key moments
2. Learn transition patterns and timing
3. Match art styles to content
4. Generate consistent visual effects
