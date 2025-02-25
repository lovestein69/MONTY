import os
import logging
from flask import Flask, request, send_file, render_template
from processors.video_processor import VideoProcessor
import config
from utils import clean_directory, save_uploaded_file, validate_clips

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

# Initialize video processor
video_processor = VideoProcessor(config.__dict__)

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html', art_packs=config.ART_PACKS)

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads and create video montage."""
    try:
        # Validate clip uploads
        if 'clips[]' not in request.files:
            logger.error("No clips uploaded")
            return 'No clips uploaded', 400

        if 'music' not in request.files:
            logger.error("No music file uploaded")
            return 'No music file uploaded', 400

        # Validate art pack selection
        art_pack = request.form.get('art_pack')
        if not art_pack or art_pack not in config.ART_PACKS:
            logger.error("Invalid art pack selected")
            return 'Please select a valid Art Pack', 400

        clips = request.files.getlist('clips[]')
        if not validate_clips(clips):
            logger.error("Invalid clips provided")
            return 'Please upload between 3 and 6 valid video clips', 400

        # Clean directories
        for folder in [config.CLIPS_FOLDER, config.ASSETS_FOLDER]:
            clean_directory(folder)

        # Save clips
        clip_paths = []
        for clip in clips:
            if clip:
                path = save_uploaded_file(clip, config.CLIPS_FOLDER)
                clip_paths.append(path)

        # Save music file
        music = request.files['music']
        music_path = save_uploaded_file(music, config.ASSETS_FOLDER, 'background.mp3')

        # Create montage with selected art pack
        duration = video_processor.create_montage(
            config.CLIPS_FOLDER,
            'assets/intro.mp4',
            'assets/outro.mp4',
            music_path,
            'output_montage.mp4',
            art_pack
        )

        logger.info(f"Montage created successfully, duration: {duration}s")

        return send_file(
            'output_montage.mp4',
            as_attachment=True,
            download_name='montage.mp4'
        )

    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)