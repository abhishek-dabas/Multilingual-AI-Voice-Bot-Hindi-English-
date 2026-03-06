"""
player.py
=========

This module is responsible for playing TTS audio
and stopping it immediately when barge-in occurs.

Key requirements:
- Non-blocking playback
- Immediate stop capability
"""

import sounddevice as sd
import soundfile as sf
import threading
import os

# Global playback control
_playback_thread = None
_stop_event = threading.Event()


def _play_audio_worker(audio_file: str):
    """
    Internal worker function that runs in a separate thread
    to play audio.
    """
    try:
        
        # Read audio file (mp3/wav supported by soundfile)
        data, samplerate = sf.read(audio_file, dtype="float32")

        # Clear stop flag before playback
        _stop_event.clear()

        # Play audio
        sd.play(data, samplerate)

        # Wait until playback finishes OR stop event is triggered
        while sd.get_stream().active:
            if _stop_event.is_set():
                sd.stop()
                break
        
        if os.path.exists(audio_file):
            os.remove(audio_file)

    except Exception as e:
        print(f"❌ Audio playback error: {e}")


def play_audio(audio_file: str):
    """
    Plays an audio file asynchronously (non-blocking).

    Args:
        audio_file (str): Path to audio file
    """
    global _playback_thread

    # If something is already playing, stop it first
    stop_audio()

    # Start new playback thread
    _playback_thread = threading.Thread(
        target=_play_audio_worker,
        args=(audio_file,),
        daemon=True
    )
    _playback_thread.start()


def stop_audio():
    """
    Immediately stops audio playback.
    Used for barge-in handling.
    """
    _stop_event.set()
    try:
        sd.stop()
    except Exception:
        pass
