import os
print("Loading custom_functions.py from:", os.path.abspath(__file__))

print("Debug - Initializing empty ContextData class...")
class ContextData:
    """Empty class kept for backwards compatibility"""
    def __init__(self):
        print("Debug - ContextData instance created")
        pass
