import torch
import numpy as np

model, utils = torch.hub.load( # It loads pretrained Silero VAD. Offline, no API calls
    repo_or_dir='snakers4/silero-vad',
    model='silero_vad',
    trust_repo=True
)

(get_speech_timestamps, _, _, _, _) = utils

#def is_speech(audio_chunk): # Core function used to detect user speech start, detect speech end and detect barge-in
#    audio = np.squeeze(audio_chunk)
#    timestamps = get_speech_timestamps(audio, model, sampling_rate=16000)
#    return len(timestamps) > 0 # If speech exists -> return True

def is_speech(audio_chunk):
    # Convert to torch tensor (CRITICAL)
    audio = torch.from_numpy(
        np.asarray(audio_chunk, dtype=np.float32).squeeze()
    )

    # Normalize for VAD
    max_val = torch.max(torch.abs(audio))
    if max_val > 0:
        audio = audio / max_val

    timestamps = get_speech_timestamps(
        audio,
        model,
        sampling_rate=16000
    )

    return len(timestamps) > 0

