import cv2
import logging
import os
import subprocess
import numpy as np
from typing import Dict, List, Tuple, Optional
from .filter_processor import FilterProcessor
from .audio_processor import AudioProcessor

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self, config: Dict):
        self.config = config
        self.filter_processor = FilterProcessor(config)
        self.audio_processor = AudioProcessor()

    def get_video_info(self, video_path: str) -> Dict:
        """Get basic video metadata."""
        logger.info(f"Analyzing video: {video_path}")
        cap = cv2.VideoCapture(video_path)
        
        try:
            info = {
                'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': cap.get(cv2.CAP_PROP_FPS),
                'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
            }
            logger.debug(f"Video info: {info}")
            return info
        finally:
            cap.release()

    def create_montage(
        self,
        clip_folder: str,
        intro_file: str,
        outro_file: str,
        music_file: str,
        output_path: str
    ) -> float:
        """Create video montage with beat-synchronized transitions."""
        video_files = [f for f in os.listdir(clip_folder)
                      if f.endswith(('.mp4', '.avi', '.mov'))]
        
        if not (3 <= len(video_files) <= 6):
            raise ValueError("Please provide 3 to 6 clips")
        
        video_files = [os.path.join(clip_folder, f) for f in video_files]
        all_clips = [intro_file] + video_files + [outro_file]
        
        # Analyze audio beats
        beat_times = self.audio_processor.analyze_beats(music_file)
        logger.info(f"Detected {len(beat_times)} beats in the music")
        
        return self._process_videos(all_clips, beat_times, music_file, output_path)

    def _process_videos(
        self,
        clips: List[str],
        beat_times: np.ndarray,
        music_file: str,
        output_path: str
    ) -> float:
        """Process and combine video clips."""
        temp_output = f"{output_path}.temp.avi"
        
        try:
            # Setup video writer based on first clip
            writer_params = self._setup_video_writer(clips[0], temp_output)
            if not writer_params['writer'].isOpened():
                raise RuntimeError("Failed to create video writer")

            current_time = 0.0
            prev_frames = []

            # Process each clip
            for i, video_file in enumerate(clips):
                self._process_clip(
                    video_file,
                    i,
                    current_time,
                    writer_params,
                    prev_frames
                )
                current_time += writer_params['clip_duration']

            writer_params['writer'].release()

            # Add audio
            self._add_audio(temp_output, music_file, output_path)
            
            final_info = self.get_video_info(output_path)
            logger.info(f"Montage created successfully! Duration: {final_info['duration']:.2f}s")
            return final_info['duration']

        except Exception as e:
            logger.error(f"Error creating montage: {str(e)}")
            raise
        finally:
            if os.path.exists(temp_output):
                os.remove(temp_output)

    def _setup_video_writer(
        self,
        first_clip: str,
        output_path: str
    ) -> Dict:
        """Setup video writer with parameters from first clip."""
        cap = cv2.VideoCapture(first_clip)
        params = {
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'clip_duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS),
            'writer': cv2.VideoWriter(
                output_path,
                cv2.VideoWriter_fourcc(*'XVID'),
                cap.get(cv2.CAP_PROP_FPS),
                (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                 int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            )
        }
        cap.release()
        return params

    def _process_clip(
        self,
        video_file: str,
        index: int,
        current_time: float,
        writer_params: Dict,
        prev_frames: List[np.ndarray]
    ) -> None:
        """Process individual video clip."""
        logger.info(f"Processing: {video_file}")
        cap = cv2.VideoCapture(video_file)
        frame_count = 0
        
        filter_name = ['warm', 'cool', 'cinematic'][index % 3]
        logger.debug(f"Applying filter: {filter_name}")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = self._process_frame(
                frame,
                frame_count,
                current_time,
                writer_params,
                filter_name,
                prev_frames
            )
            
            writer_params['writer'].write(frame)
            frame_count += 1
            
            if frame_count % 100 == 0:
                logger.debug(f"Processed {frame_count} frames...")
        
        cap.release()
        logger.info(f"Completed {video_file}: {frame_count} frames")

    def _process_frame(
        self,
        frame: np.ndarray,
        frame_count: int,
        current_time: float,
        writer_params: Dict,
        filter_name: str,
        prev_frames: List[np.ndarray]
    ) -> np.ndarray:
        """Process individual frame with filters and transitions."""
        if frame.shape[:2] != (writer_params['height'], writer_params['width']):
            frame = cv2.resize(frame, (writer_params['width'], writer_params['height']))
        
        frame = self.filter_processor.process_frame(frame, filter_name)
        
        frame_time = current_time + (frame_count / writer_params['fps'])
        nearest_beat = self.audio_processor.get_nearest_beat(frame_time)
        
        if nearest_beat is not None and prev_frames:
            beat_distance = abs(frame_time - nearest_beat)
            if beat_distance < (self.config['TRANSITION_DURATION'] / 2):
                frame = self._apply_transition(
                    frame,
                    prev_frames,
                    frame_count,
                    beat_distance
                )
        
        return frame

    def _apply_transition(
        self,
        frame: np.ndarray,
        prev_frames: List[np.ndarray],
        frame_count: int,
        beat_distance: float
    ) -> np.ndarray:
        """Apply transition effect between frames."""
        alpha = 1.0 - (beat_distance / (self.config['TRANSITION_DURATION'] / 2))
        frame_idx = min(len(prev_frames) - 1, frame_count)
        
        if frame_idx < len(prev_frames):
            return cv2.addWeighted(
                prev_frames[frame_idx],
                1.0 - alpha,
                frame,
                alpha,
                0
            )
        return frame

    def _add_audio(
        self,
        video_path: str,
        audio_path: str,
        output_path: str
    ) -> None:
        """Add background audio to video using FFmpeg."""
        logger.info("Adding background audio...")
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-c:a', 'aac',
            '-shortest',
            output_path
        ]
        
        subprocess.run(cmd, check=True)
