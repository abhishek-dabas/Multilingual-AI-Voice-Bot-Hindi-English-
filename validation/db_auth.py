USERS = [
    {"mobile": "9876543210", "dob": "2000-01-01", "name": "Rahul"},
    {"mobile": "1234567890", "dob": "1996-02-02", "name": "Anita"},
]
# In-memory DB

def validate_user(mobile, dob): # Clean separation and easy to replace with real DB later
    for user in USERS:
        if user["mobile"] == mobile and user["dob"] == dob:
            return True, user
    return False, None
