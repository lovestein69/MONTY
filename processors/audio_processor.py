import os
import numpy as np
from scipy.io import wavfile
from scipy import signal
import subprocess
from typing import Optional, List, Union
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AudioProcessor:
    def __init__(self):
        self.tempo: Optional[float] = None
        self.beat_frames: Optional[np.ndarray] = None
        self.beat_times: Optional[np.ndarray] = None

    def convert_to_wav(self, audio_file: str) -> str:
        """Convert audio file to WAV format for processing"""
        wav_file = f"{audio_file}.wav"
        cmd = [
            'ffmpeg', '-y',
            '-i', audio_file,
            '-acodec', 'pcm_s16le',
            '-ar', '44100',
            wav_file
        ]
        subprocess.run(cmd, capture_output=True)
        return wav_file

    def generate_default_beats(self, duration: float, bpm: int = 120) -> np.ndarray:
        """Generate evenly spaced beats at specified BPM"""
        self.tempo = bpm
        beat_interval = 60.0 / bpm
        self.beat_times = np.arange(0, duration, beat_interval)
        logger.info(f"Generated {len(self.beat_times)} beats at {bpm} BPM")
        return self.beat_times

    def analyze_beats(self, audio_file: str) -> np.ndarray:
        """Analyze audio file for beats using scipy"""
        logger.info(f"Analyzing beats in audio file: {audio_file}")

        try:
            wav_file = self.convert_to_wav(audio_file)
            sample_rate, audio_data = wavfile.read(wav_file)

            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)

            audio_data = self._normalize_audio(audio_data)
            onset_env = self._compute_onset_envelope(audio_data, sample_rate)
            self.beat_times = self._detect_beats(onset_env, sample_rate)

            if os.path.exists(wav_file):
                os.remove(wav_file)

            return self.beat_times

        except Exception as e:
            logger.error(f"Error analyzing beats: {str(e)}")
            if 'wav_file' in locals() and os.path.exists(wav_file):
                os.remove(wav_file)
            return self.generate_default_beats(69)

    def _normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Normalize audio data to float32 between -1 and 1"""
        if audio_data.dtype.kind in 'iu':
            return audio_data.astype(np.float32) / np.iinfo(audio_data.dtype).max
        audio_data = audio_data.astype(np.float32)
        return audio_data / np.abs(audio_data).max()

    def _compute_onset_envelope(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Compute onset strength envelope"""
        window_size = int(0.05 * sample_rate)
        hop_length = window_size // 2

        onset_env = []
        for i in range(0, len(audio_data) - window_size, hop_length):
            window = audio_data[i:i + window_size]
            rms = np.sqrt(np.mean(window**2))
            onset_env.append(rms)

        onset_env = np.array(onset_env)
        if onset_env.max() > 0:
            onset_env /= onset_env.max()
        return onset_env

    def get_nearest_beat(self, time_point: float) -> Optional[float]:
        """Find the nearest beat to a given time point"""
        if self.beat_times is None or len(self.beat_times) == 0:
            return None
        return self.beat_times[np.argmin(np.abs(self.beat_times - time_point))]

    def get_beats_in_range(self, start_time: float, end_time: float) -> np.ndarray:
        """Get all beats within a time range"""
        if self.beat_times is None or len(self.beat_times) == 0:
            return np.array([])
        mask = (self.beat_times >= start_time) & (self.beat_times <= end_time)
        return self.beat_times[mask]
