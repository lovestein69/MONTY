import os
import numpy as np
import logging
import subprocess
from typing import Optional, List
from scipy.io import wavfile
from scipy import signal

logger = logging.getLogger(__name__)

class AudioProcessor:
    def __init__(self):
        self.tempo: Optional[float] = None
        self.beat_frames: Optional[np.ndarray] = None
        self.beat_times: Optional[np.ndarray] = None

    def convert_to_wav(self, audio_file: str) -> str:
        """Convert audio file to WAV format for processing."""
        wav_file = f"{audio_file}.wav"
        cmd = [
            'ffmpeg', '-y',
            '-i', audio_file,
            '-acodec', 'pcm_s16le',
            '-ar', '44100',
            wav_file
        ]
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            logger.debug(f"Converted {audio_file} to WAV")
            return wav_file
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg conversion failed: {str(e)}")
            raise

    def generate_default_beats(self, duration: float, bpm: float = 120) -> np.ndarray:
        """Generate evenly spaced beats at specified BPM."""
        self.tempo = bpm
        beat_interval = 60.0 / bpm
        self.beat_times = np.arange(0, duration, beat_interval)
        logger.debug(f"Generated {len(self.beat_times)} beats at {bpm} BPM")
        return self.beat_times

    def analyze_beats(self, audio_file: str) -> np.ndarray:
        """Analyze audio file for beats using scipy."""
        logger.info(f"Analyzing beats in audio file: {audio_file}")
        wav_file = None

        try:
            wav_file = self.convert_to_wav(audio_file)
            sample_rate, audio_data = wavfile.read(wav_file)

            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)

            # Normalize audio data
            audio_data = self._normalize_audio(audio_data)

            # Process onset envelope
            onset_env = self._calculate_onset_envelope(audio_data, sample_rate)
            
            # Find peaks
            peaks = self._find_beat_peaks(onset_env, sample_rate)
            
            self.beat_times = peaks * (len(audio_data) / len(onset_env)) / sample_rate

            if len(self.beat_times) == 0:
                logger.warning("No beats detected, using default beat generation")
                duration = len(audio_data) / sample_rate
                return self.generate_default_beats(duration)

            # Calculate tempo
            beat_intervals = np.diff(self.beat_times)
            self.tempo = 60 / np.median(beat_intervals)
            
            logger.info(f"Detected tempo: {self.tempo:.2f} BPM")
            logger.info(f"Found {len(self.beat_times)} beats")
            
            return self.beat_times

        except Exception as e:
            logger.error(f"Error analyzing beats: {str(e)}")
            return self.generate_default_beats(69)
        
        finally:
            if wav_file and os.path.exists(wav_file):
                os.remove(wav_file)

    def _normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Normalize audio data to float32 between -1 and 1."""
        audio_data = audio_data.astype(np.float32)
        if audio_data.dtype.kind in 'iu':
            audio_data /= np.iinfo(audio_data.dtype).max
        else:
            audio_data /= np.abs(audio_data).max()
        return audio_data

    def _calculate_onset_envelope(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Calculate onset envelope from audio data."""
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

    def _find_beat_peaks(self, onset_env: np.ndarray, sample_rate: int) -> np.ndarray:
        """Find peaks in onset envelope that correspond to beats."""
        min_samples_between_beats = int(60 / 180 * sample_rate / len(onset_env) * 2)
        return signal.find_peaks(
            onset_env,
            distance=min_samples_between_beats,
            prominence=0.1
        )[0]

    def get_nearest_beat(self, time_point: float) -> Optional[float]:
        """Get the nearest beat to a given time point."""
        if self.beat_times is None or len(self.beat_times) == 0:
            return None
        return self.beat_times[np.argmin(np.abs(self.beat_times - time_point))]

    def get_beats_in_range(self, start_time: float, end_time: float) -> np.ndarray:
        """Get all beats within a time range."""
        if self.beat_times is None or len(self.beat_times) == 0:
            return np.array([])
        mask = (self.beat_times >= start_time) & (self.beat_times <= end_time)
        return self.beat_times[mask]
