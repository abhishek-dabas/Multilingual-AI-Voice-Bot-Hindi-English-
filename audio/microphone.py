import sounddevice as sd
import queue
import numpy as np

SAMPLE_RATE = 16000
CHANNELS = 1
BLOCK_SIZE = 1024   # IMPORTANT

audio_queue = queue.Queue()

def audio_callback(indata, frames, time_info, status):
    # Force mono + correct shape
    chunk = np.asarray(indata[:, 0], dtype=np.float32).copy()
    audio_queue.put(chunk)

def start_microphone():
    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        blocksize=BLOCK_SIZE,
        dtype="float32",
        callback=audio_callback
    )
    stream.start()
    return stream
