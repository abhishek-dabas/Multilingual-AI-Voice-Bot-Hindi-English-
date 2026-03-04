🧠 Multilingual Real-Time Voice Bot (Hindi + English)

📌 Overview

This project is a working prototype of a real-time multilingual Voice AI system supporting:

1. English + Hindi voice interaction
2. Code-mixed queries (e.g., “Hi, mera policy status check kar do”)
3. DB-based user validation
4. Logical barge-in (interruption handling)
5. Latency measurement
6. Background noise tolerance

The focus of this implementation is conversational architecture, real-time orchestration, and system clarity, not production telephony deployment.

🚀 Features Implemented

🎙️ Real-Time Voice Interaction

- Continuous microphone stream
- VAD-based speech detection (start/stop)
- Speech-to-Text using Whisper
- Text-to-Speech response playback
- Prototype-level speaker verification module included but not fully integrated.

🔐 DB-Based Validation Flow

- In-memory database with dummy users
- Mobile number capture (spoken digits normalized)
- DOB capture and verification
- Stateful validation before answering sensitive queries

🌍 Multilingual + Code-Mixed Support

- English & Hindi supported
- Handles mixed queries like:
       - “Mera policy status check kar do”
       - “OTP aaya nahi, can you resend?”

🔁 Repeated Question Handling

- Detects previously asked question
- Responds with contextual repeat acknowledgment

🛑 Logical Barge-In

- If user speaks while bot is responding:
       - Bot stops TTS
       - Switches context to new query
- Designed for local prototype constraints (Windows full-duplex limitations acknowledged)

⏱️ Latency Measurement

- System logs timestamps for:
       - ASR_end_time
       - LLM_start_time
       - TTS_start_time
       - Audio_first_byte_time
- These logs allow rough computation of:
       - Average latency
       - P95 latency

🔊 Background Noise Tolerance

- Energy-threshold tuning in VAD
- Speech buffering logic
- Demonstrated functionality under artificial background noise

🏗️ Architecture Overview

Microphone Input
       ↓
Voice Activity Detection (VAD)
       ↓
Speech Buffering
       ↓
ASR (Whisper)
       ↓
Validation Flow / FAQ Router
       ↓
Filler Injection (Thinking State Only)
       ↓
TTS Generation
       ↓
Audio Playback

⚠️ Assumptions & Limitations

- This is a prototype, not a production-grade telephony system.
- Logical barge-in implemented (true acoustic barge-in requires echo cancellation stack).
- Hindi ASR accuracy may vary depending on accent/environment.
- Validation uses in-memory DB (no external persistence).
- Prototype focuses on architecture and flow rather than production-grade speech accuracy.

▶️ How to Run

pip install -r requirements.txt
python main.py

🎯 Purpose

This project demonstrates:
       - Real-time voice orchestration
       - Conversational state management
       - Multilingual intent handling
       - Latency awareness
       - System-level engineering thinking