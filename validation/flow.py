# validation/flow.py

from validation.state import validation_state
from validation.db_auth import validate_user

def extract_digits(text: str, max_len: int = 10) -> str:
    """
    Extract digits from ASR text safely.
    - Supports spoken numbers
    - HARD caps length to avoid ASR hallucination
    """

    NUMBER_WORDS = {
        "zero": "0",
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
    }

    digits = []

    for word in text.lower().replace(",", "").split():
        if word.isdigit():
            digits.append(word)
        elif word in NUMBER_WORDS:
            digits.append(NUMBER_WORDS[word])

        # HARD STOP — THIS IS THE KEY
        if len(digits) == max_len:
            break

    return "".join(digits)

def normalize_dob(dob_digits: str) -> str:
    """
    Converts DDMMYYYY to YYYY-MM-DD
    Example: 01011995 → 1995-01-01
    """
    day = dob_digits[:2]
    month = dob_digits[2:4]
    year = dob_digits[4:]
    return f"{year}-{month}-{day}"

def handle_validation(text: str, lang: str) -> str | None:
    """
    Handles DB-based validation conversation.
    Returns response text if validation flow is active,
    else returns None (normal conversation continues).
    """

    text = text.lower().strip()

    # Trigger validation
    if validation_state.state == "NONE":
        if (
            "login" in text 
            or "verify" in text
            or "policy" in text
            or "claim" in text
            or "premium" in text    
            ):
            validation_state.state = "ASK_MOBILE"
            return (
                "Please tell me your registered mobile number."
                if lang == "en"
                else "Kripya apna registered mobile number batayein."
            )
        return None

    # Capture mobile number
    if validation_state.state == "ASK_MOBILE":
        # digits = "".join(ch for ch in text if ch.isdigit())
        digits = extract_digits(text)
        if len(digits) == 10:
            validation_state.mobile = digits
            validation_state.state = "ASK_DOB"
            return (
                "Please tell me your date of birth in DDMMYYYY format."
                if lang == "en"
                else "Kripya apni janam tithi DDMMYYYY format mein batayein."
            )
        else:
            return (
                "That doesn't look like a valid mobile number. Please repeat."
                if lang == "en"
                else "Yeh sahi mobile number nahi lag raha. Kripya dobara batayein."
            )

    # Capture DOB
    if validation_state.state == "ASK_DOB":
        digits = "".join(ch for ch in text if ch.isdigit())
        if len(digits) == 8:
            normalized_dob = normalize_dob(digits)
            validation_state.dob = normalized_dob

            valid, user = validate_user(
                mobile=validation_state.mobile,
                dob=normalized_dob
            )


            if valid:
                validation_state.state = "VERIFIED"
                return (
                    f"Verification successful. Welcome {user['name']}."
                    if lang == "en"
                    else f"Verification safal rahi. Swagat hai {user['name']}."
                )
            else:
                validation_state.reset()
                return (
                    "Verification failed. Please try again."
                    if lang == "en"
                    else "Verification asafal rahi. Kripya dobara koshish karein."
                )

        else:
            return (
                "That doesn't look like a valid date of birth. Please repeat."
                if lang == "en"
                else "Yeh sahi janam tithi nahi lag rahi. Kripya dobara batayein."
            )

    return None
