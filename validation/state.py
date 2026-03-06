# validation/state.py

class ValidationState:
    def __init__(self):
        self.state = "NONE"
        self.mobile = None
        self.dob = None

    def reset(self):
        self.state = "NONE"
        self.mobile = None
        self.dob = None


# Global state instance
validation_state = ValidationState()