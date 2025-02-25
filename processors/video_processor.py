import cv2
import os
import subprocess
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from .filter_processor import FilterProcessor
from .audio_processor import AudioProcessor

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self, config: Dict):
        self.config = config
        self.effects = FilterProcessor(config)
        self.audio_proc = AudioProcessor()

    def get_video_info(self, video_path: str) -> Dict[str, float]:
        """Get basic video metadata"""
        logger.info(f"Analyzing video: {video_path}")
        cap = cv2.VideoCapture(video_path)
        
        info = {
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
        }
        
        cap.release()
        return info

    def create_montage(self, 
                      clip_folder: str, 
                      intro_file: str, 
                      outro_file: str, 
                      music_file: str, 
                      output_path: str) -> float:
        """Create video montage with beat-synchronized transitions"""
        video_files = [os.path.join(clip_folder, f) for f in os.listdir(clip_folder)
                      if f.endswith(('.mp4', '.avi', '.mov'))]
        
        if not (3 <= len(video_files) <= 6):
            raise ValueError("Please provide 3 to 6 clips")
        
        all_clips = [intro_file] + video_files + [outro_file]
        beat_times = self.audio_proc.analyze_beats(music_file)
        
        try:
            dimensions = self._initialize_video_writer(all_clips[0])
            if not dimensions:
                raise RuntimeError("Failed to get video dimensions")
                
            frame_width, frame_height, fps, out = dimensions
            temp_output = f"{output_path}.temp.avi"
            
            self._process_clips(all_clips, out, frame_width, frame_height, fps, beat_times)
            out.release()
            
            self._add_audio(temp_output, music_file, output_path)
            os.remove(temp_output)
            
            final_info = self.get_video_info(output_path)
            return final_info['duration']
            
        except Exception as e:
            logger.error(f"Error creating montage: {str(e)}")
            if 'temp_output' in locals() and os.path.exists(temp_output):
                os.remove(temp_output)
            raise

    def _initialize_video_writer(self, first_video: str) -> Optional[Tuple[int, int, float, cv2.VideoWriter]]:
        """Initialize video writer with parameters from first video"""
        cap = cv2.VideoCapture(first_video)
        if not cap.isOpened():
            return None
            
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(
            f"{self.config['output_path']}.temp.avi",
            fourcc, 
            fps,
            (frame_width, frame_height)
        )
        
        return frame_width, frame_height, fps, out

    def _process_clips(self, 
                      clips: List[str], 
                      out: cv2.VideoWriter,
                      frame_width: int,
                      frame_height: int,
                      fps: float,
                      beat_times: np.ndarray) -> None:
        """Process each video clip and apply effects"""
        current_time = 0.0
        prev_frames = []
        
        for i, video_file in enumerate(clips):
            logger.info(f"Processing: {video_file}")
            cap = cv2.VideoCapture(video_file)
            frame_count = 0
            
            filter_name = ['warm', 'cool', 'cinematic'][i % 3]
            clip_duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps
            clip_beats = self.audio_proc.get_beats_in_range(current_time, 
                                                          current_time + clip_duration)
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame = self._process_frame(frame, frame_count, current_time, fps,
                                         frame_width, frame_height, filter_name,
                                         prev_frames, i)
                
                out.write(frame)
                frame_count += 1
                
                if frame_count % 100 == 0:
                    logger.info(f"Processed {frame_count} frames...")
            
            current_time += clip_duration
            cap.release()

    def _add_audio(self, temp_output: str, music_file: str, output_path: str) -> None:
        """Add background audio to the video"""
        logger.info("Adding background audio...")
        cmd = [
            'ffmpeg', '-y',
            '-i', temp_output,
            '-i', music_file,
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-c:a', 'aac',
            '-shortest',
            output_path
        ]
        subprocess.run(cmd)
