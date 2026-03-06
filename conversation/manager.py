# conversation/manager.py

import json
import os
from conversation.memory import memory

# Load FAQs once
FAQ_PATH = os.path.join(os.path.dirname(__file__), "faqs.json")

with open(FAQ_PATH, "r", encoding="utf-8") as f:
    FAQS = json.load(f)


# Simple keyword → intent mapping
INTENT_KEYWORDS = {
    "policy_status": [
        # English
        "policy status", "policy", "status",
        # Hindi / Hinglish
        "policy ka status", "policy status batao", "mera policy status",
        "policy kya hai", "policy check", "status batao"
    ],

    "policy_expiry": [
        "expiry", "expire",
        "policy kab khatam", "policy expire", "expiry date"
    ],

    "premium_amount": [
        "premium", "amount",
        "premium kitna", "premium amount", "kitna premium"
    ],

    "claim_status": [
        "claim status", "claim",
        "mera claim", "claim ka status", "claim batao"
    ],

    "claim_process": [
        "raise claim", "claim process",
        "claim kaise kare", "claim ka process"
    ],

    "customer_care": [
        "customer care", "support", "helpline",
        "customer care number", "help chahiye"
    ],

    "update_mobile": [
        "update mobile", "change number",
        "mobile change", "number update"
    ],

    "otp_not_received": [
        "otp", "not received", "resend otp",
        "otp nahi aaya", "otp dobara bhejo"
    ],

    "policy_document": [
        "policy document", "document",
        "policy paper", "policy document bhejo"
    ],

    "greeting": [
        "hello", "hi", "namaste",
        "hey", "good morning"
    ]
}

def infer_response_language(text: str, asr_lang: str) -> str:
    text = text.lower()

    # Strong Hindi indicators (grammar words, not domain words)
    hindi_markers = [
        "mera", "meri", "aap", "tum", "kya", "ka", "ki",
        "hai", "nahi", "batao", "kar do", "chahiye"
    ]

    for word in hindi_markers:
        if word in text:
            return "hi"

    # If Whisper clearly says English, trust it
    if asr_lang == "en":
        return "en"

    # Default fallback
    return "en"
"""
def detect_intent(text: str) -> str | None:
    """
"""
    Detect intent based on keywords.
    """
"""
    text = text.lower().strip()
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return intent
    return None
"""
def detect_intent(text: str) -> str | None:
    text = text.lower()

    # Policy status intent: very forgiving
    if "policy" in text and "status" in text:
        return "policy_status"

    if "policy" in text and ("expire" in text or "expiry" in text):
        return "policy_expiry"

    if "premium" in text:
        return "premium_amount"

    if "claim" in text and "status" in text:
        return "claim_status"

    if "claim" in text:
        return "claim_process"

    if "otp" in text:
        return "otp_not_received"

    if "hello" in text or "hi" in text or "namaste" in text:
        return "greeting"
    
    if "benefits" in text.lower():
        return (
        "Sure. Let me explain your insurance policy benefits in detail. "
        "Your policy includes hospitalization coverage, cashless treatment, "
        "pre and post hospitalization expenses, and several additional riders. "
        "Please listen carefully while I explain each benefit one by one."
    )

    return None

def answer_question(text: str, lang: str) -> str:
    """
    Returns FAQ answer based on detected intent and language.
    """
    lang = infer_response_language(text, lang)
    intent = detect_intent(text)

    # Unknown intent
    if not intent:
        return (
            "Sorry, I didn’t understand your question."
            if lang == "en"
            else "Maaf kijiye, main aapki baat samajh nahi paaya."
        )

    
    # Repeated question handling
    is_repeat = memory.is_repeat(intent)

    answer = FAQS.get(intent, {}).get(lang)

    if not answer:
        return (
            "Sorry, this information is not available right now."
            if lang == "en"
            else "Maaf kijiye, yeh jaankari abhi uplabdh nahi hai."
        )

    if is_repeat:
        repeat_prefix = (
            "You already asked that. Let me repeat. "
            if lang == "en"
            else "Aap yeh sawaal pehle bhi pooch chuke hain. Main dobara bata deta hoon. "
        )
        return repeat_prefix + answer

    return answer
