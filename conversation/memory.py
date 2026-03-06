# conversation/memory.py

class ConversationMemory:
    def __init__(self):
        self.last_intent = None

    def is_repeat(self, intent):
        """
        Checks if the user is repeating the same question.
        """
        if intent == self.last_intent:
            return True
        self.last_intent = intent
        return False


# global memory instance
memory = ConversationMemory()