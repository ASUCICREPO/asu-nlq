import time
from datetime import datetime

class Timer:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.start_time = time.perf_counter()
            cls._instance.last_checkpoint_time = cls._instance.start_time
        return cls._instance
    
    def checkpoint(self, label):
        current_time = time.perf_counter()
        total_elapsed = current_time - self.start_time
        checkpoint_elapsed = current_time - self.last_checkpoint_time
        
        message = f"{label} (Total: +{total_elapsed:.3f}s, Checkpoint: +{checkpoint_elapsed:.3f}s)"
        
        # Update last checkpoint time for next call
        self.last_checkpoint_time = current_time
        return message
    
    def reset(self):
        """Reset the timer for a new execution"""
        self.start_time = time.perf_counter()
        self.last_checkpoint_time = self.start_time

# Create the singleton instance at module level
timer = Timer()