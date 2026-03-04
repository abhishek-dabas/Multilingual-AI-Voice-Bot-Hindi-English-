"""
main.py
========
This file is the ORCHESTRATOR of the Multilingual Voice Bot.

Responsibilities of this file:
- Start microphone input
- Continuously listen to user speech
- Detect speech start / end using VAD
- Handle barge-in (user interrupting bot)
- Run ASR (Speech → Text)
- Route validation logic
- Run conversation logic (FAQ / responses)
- Generate TTS output
- Play TTS audio with interruption support
- Measure and log latency at each stage
"""

# -----------------------------
# Standard Python imports
# -----------------------------
import time
import threading
import numpy as np

# -----------------------------
# Audio-related imports
# -----------------------------
from audio.microphone import start_microphone, audio_queue
from audio.vad import is_speech
from audio.player import play_audio, stop_audio

# -----------------------------
# ASR (Speech-to-Text)
# -----------------------------
from asr.speech_to_text import transcribe

# -----------------------------
# Validation modules
# -----------------------------
from validation.flow import handle_validation

# -----------------------------
# Conversation logic
# -----------------------------
from conversation.manager import answer_question
from conversation.fillers import maybe_add_filler

# -----------------------------
# TTS (Text-to-Speech)
# -----------------------------
from tts.text_to_speech import synthesize_speech

# -----------------------------
# Latency tracking
# -----------------------------
from metrics.latency import LatencyTracker

# ============================================================
# GLOBAL STATE VARIABLES
# ============================================================

# Flag to indicate whether the bot is currently speaking.
bot_speaking = False

# Controls the main loop.
conversation_active = True

# Latency tracker object (stores timestamps)
latency = LatencyTracker()

# -----------------------------
# VAD-based buffering state
# -----------------------------
speech_buffer = []
silence_counter = 0

ENERGY_THRESHOLD = 0.0005     # speech vs silence, minimum energy to treat as speech
MAX_SILENCE_CHUNKS = 15        # ~0.5 sec silence → end of speech
#MIN_SPEECH_SAMPLES = 16000    # at least 1 sec of speech
MIN_SPEECH_CHUNKS = 15   # ≈ 1 second (15 * 1024 samples)
MAX_SPEECH_CHUNKS = 80        # ~3 seconds max speech
END_SILENCE_THRESHOLD = 0.0008  # stricter silence to end speech

# ============================================================
# MAIN FUNCTION
# ============================================================

def main():
    global bot_speaking
    # global audio_buffer
    global conversation_active
    global silence_counter        
    global speech_buffer          

    print("🎤 Voice Bot starting...")
    print("Speak anytime. Press Ctrl+C to exit.\n")

    # --------------------------------------------------------
    # Start microphone stream (non-blocking)
    # --------------------------------------------------------
    mic_stream = start_microphone()

    def play_tts_async(audio_file):
        """
        Plays TTS audio in a separate thread so mic loop stays alive.
        """
        global bot_speaking

        def _play():
            global bot_speaking
            bot_speaking = True
            play_audio(audio_file)
            bot_speaking = False

        t = threading.Thread(target=_play, daemon=True)
        t.start()

    try:
        # ----------------------------------------------------
        # Main event loop (runs forever until Ctrl+C)
        # ----------------------------------------------------
        while conversation_active:

            # ------------------------------------------------
            # Check if new audio data is available
            # ------------------------------------------------
            if not audio_queue.empty():

                # Get one chunk of audio from the queue
                chunk = audio_queue.get()

                # --------------------------------------------
                # BARGE-IN LOGIC
                # --------------------------------------------
                # If the bot is speaking AND user speech is detected,
                # immediately stop TTS and switch to listening mode.

                if bot_speaking and is_speech(chunk):
                    print("🛑 BARGE-IN DETECTED! User interrupted the bot.")

                    # Stop current TTS immediately
                    stop_audio()
                    bot_speaking = False

                    # Reset buffers to capture new intent
                    speech_buffer.clear()
                    silence_counter = 0

                    # Provide immediate acknowledgement of interruption
                    interrupt_response = "Haan, bolo. Aapka naya sawaal kya hai?"
                    audio_file = synthesize_speech(interrupt_response, "hi")
                    play_audio(audio_file)

                    continue  

                # -----------------------------
                # Energy-based VAD
                # -----------------------------
                energy = np.mean(np.abs(chunk))

                if energy > ENERGY_THRESHOLD:
                    silence_counter = 0
                    #speech_buffer.extend(chunk)
                    speech_buffer.append(chunk)

                else:
                    # Silence candidate
                    if energy < END_SILENCE_THRESHOLD:
                        silence_counter += 1
                    else:
                        # Noise but not speech → don't reset silence completely
                        silence_counter += 1

                # If user stopped speaking AND we have enough speech
                if (
                    (silence_counter >= MAX_SILENCE_CHUNKS and len(speech_buffer) >= MIN_SPEECH_CHUNKS)
                    or len(speech_buffer) >= MAX_SPEECH_CHUNKS
                ):

                    print("⏹️  Speech ended. Triggering ASR...")
                    print("🧠 Processing user input...")

                    audio_np = np.concatenate(speech_buffer).astype(np.float32)

                    # Reset buffers
                    speech_buffer = []
                    silence_counter = 0

                    # ----------------------------
                    # ASR
                    # ----------------------------
                    latency.mark("ASR_start_time")
                    text, lang = transcribe(audio_np)
                    latency.mark("ASR_end_time")

                    if lang not in ["hi", "en"]:
                        lang = "hi"

                    print(f"🗣️  User said: {text} (language={lang})")

                    # ------------------------------------------------
                    # LOGICAL BARGE-IN (INTENT-BASED)
                    # ------------------------------------------------
                    if any(
                        phrase in text.lower()
                        for phrase in ["wait", "stop", "ruk", "ek minute", "one minute"]
                    ):
                        print("🛑 LOGICAL BARGE-IN TRIGGERED")

                        stop_audio()
                        bot_speaking = False

                        response_text = (
                            "Haan, bolo. Aap apna naya sawaal pooch sakte hain."
                            if lang == "hi"
                            else "Okay, please ask your new question."
                        )

                        print(f"🤖 Bot response ({lang}): {response_text}")

                        audio_file = synthesize_speech(response_text, lang)
                        play_tts_async(audio_file)

                        continue

                    # ----------------------------
                    # Conversation logic
                    # ----------------------------
                    latency.mark("LLM_start_time")

                    # Validation flow has priority
                    validation_response = handle_validation(text, lang)

                    if validation_response:
                        response_text = validation_response
                    else:
                        response_text = answer_question(text, lang)


                    if text.strip():
                        response_text = maybe_add_filler(response_text, lang, thinking=True)
                    latency.mark("LLM_end_time")

                    # ----------------------------
                    # TTS
                    # ----------------------------
                    latency.mark("TTS_start_time")

                    print(f"🤖 Bot response ({lang}): {response_text}")

                    audio_file = synthesize_speech(response_text, lang)
                    latency.mark("Audio_first_byte_time")

                    play_tts_async(audio_file)

                    # ----------------------------
                    # Latency report
                    # ----------------------------
                    print("\n⏱️  Latency Metrics:")
                    latency.report()
                    print("-" * 40)

                    # Flush old audio
                    while not audio_queue.empty():
                        audio_queue.get()

            # Small sleep to prevent CPU overuse
            time.sleep(0.01)
    except KeyboardInterrupt:
        # Graceful shutdown on Ctrl+C
        print("\n🛑 Shutting down Voice Bot...")
        conversation_active = False
        mic_stream.stop()

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()