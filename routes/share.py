import os
from flask import Blueprint, jsonify, request, current_app, url_for
import logging

logger = logging.getLogger(__name__)
share_bp = Blueprint('share', __name__)

@share_bp.route('/share/<montage_id>', methods=['GET'])
def get_share_link(montage_id):
    """Generate a shareable link for a montage."""
    try:
        share_url = url_for('share.view_montage', montage_id=montage_id, _external=True)
        return jsonify({
            'success': True,
            'share_url': share_url
        })
    except Exception as e:
        logger.error(f"Error generating share link: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate share link'
        }), 500

@share_bp.route('/montage/<montage_id>', methods=['GET'])
def view_montage(montage_id):
    """View a shared montage."""
    try:
        # In a real implementation, we would fetch the montage details from a database
        # For now, we'll just check if the file exists
        montage_path = os.path.join(current_app.root_path, 'uploads', f'montage_{montage_id}.mp4')
        
        if not os.path.exists(montage_path):
            return jsonify({
                'success': False,
                'error': 'Montage not found'
            }), 404

        return jsonify({
            'success': True,
            'montage_url': url_for('static', filename=f'montages/montage_{montage_id}.mp4')
        })
    except Exception as e:
        logger.error(f"Error accessing montage: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to access montage'
        }), 500

@share_bp.route('/export/<montage_id>', methods=['POST'])
def export_montage(montage_id):
    """Export a montage with specified quality settings."""
    try:
        quality = request.json.get('quality', 'high')
        
        quality_settings = {
            'high': {'resolution': '1920x1080', 'bitrate': '8M'},
            'medium': {'resolution': '1280x720', 'bitrate': '4M'},
            'low': {'resolution': '854x480', 'bitrate': '2M'}
        }
        
        settings = quality_settings.get(quality, quality_settings['high'])
        
        # Here we would process the video with the specified quality settings
        # For now, we'll just return success
        return jsonify({
            'success': True,
            'message': f'Montage exported with {quality} quality',
            'settings': settings
        })
    except Exception as e:
        logger.error(f"Error exporting montage: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to export montage'
        }), 500
