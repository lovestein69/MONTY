import os
from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename
import logging
from processors.video_processor import VideoProcessor
import config
from utils import allowed_file, ensure_directories_exist, clear_directory

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

# Ensure required directories exist
required_dirs = [app.config['UPLOAD_FOLDER'], config.CLIPS_DIR, config.ASSETS_DIR]
ensure_directories_exist(required_dirs)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        if 'clips[]' not in request.files:
            return 'No clips uploaded', 400
        
        if 'music' not in request.files:
            return 'No music file uploaded', 400

        # Validate and save clips
        clips = request.files.getlist('clips[]')
        if not (3 <= len(clips) <= 6):
            return 'Please upload between 3 and 6 video clips', 400

        # Clear previous files
        clear_directory(config.CLIPS_DIR)
        clear_directory(config.ASSETS_DIR)

        # Save new clips
        clip_paths = []
        for clip in clips:
            if clip and allowed_file(clip.filename, config.ALLOWED_EXTENSIONS):
                filename = secure_filename(clip.filename)
                path = os.path.join(config.CLIPS_DIR, filename)
                clip.save(path)
                clip_paths.append(path)

        # Save music file
        music = request.files['music']
        if music and allowed_file(music.filename, config.ALLOWED_EXTENSIONS):
            music_path = os.path.join(config.ASSETS_DIR, 'background.mp3')
            music.save(music_path)
        else:
            return 'Invalid music file', 400

        # Create montage
        video_processor = VideoProcessor(config.__dict__)
        duration = video_processor.create_montage(
            config.CLIPS_DIR,
            os.path.join(config.ASSETS_DIR, 'intro.mp4'),
            os.path.join(config.ASSETS_DIR, 'outro.mp4'),
            music_path,
            'output_montage.mp4'
        )
        
        return send_file(
            'output_montage.mp4',
            as_attachment=True,
            download_name='montage.mp4'
        )
    
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        return str(e), 500
