"""
voiceprint.py
=============

Lightweight speaker verification wrapper.

IMPORTANT:
- Speaker verification is OPTIONAL
- On Windows without admin privileges, symlinks fail
- We gracefully fallback instead of crashing
"""

def verify(enroll_wav: str, test_wav: str) -> bool:
    """
    Attempts speaker verification.

    Returns:
        True  -> speaker verified
        False -> verification failed OR unavailable
    """

    try:
        from speechbrain.pretrained import SpeakerRecognition

        spk_model = SpeakerRecognition.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir="pretrained_models/speaker_verification",
            run_opts={"device": "cpu"}
        )

        score, prediction = spk_model.verify_files(enroll_wav, test_wav)
        return bool(prediction)

    except Exception as e:
        # Windows-safe fallback
        print("⚠️ Speaker verification unavailable on this system.")
        print(f"Reason: {e}")
        print("➡️ Falling back to OTP / DB-based verification.")
        return False
