import cv2
import numpy as np
import pyautogui
import os
import threading
import time
from datetime import datetime
from utils.logger import Logger

class VideoRecorder:
    """Utility to record the screen during automation execution."""
    
    def __init__(self, output_dir="recordings", fps=8.0):
        self.output_dir = output_dir
        self.fps = fps
        self.recording = False
        self.thread = None
        self.logger = Logger().get_logger()
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _record(self, filename):
        """Internal recording loop."""
        screen_size = tuple(pyautogui.size())
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        filepath = os.path.join(self.output_dir, filename)
        out = cv2.VideoWriter(filepath, fourcc, self.fps, screen_size)
        
        self.logger.info(f"Started video recording: {filepath}")
        
        last_time = time.time()
        while self.recording:
            # Capture screen
            img = pyautogui.screenshot()
            # Convert to numpy array
            frame = np.array(img)
            # Convert from RGB to BGR (OpenCV uses BGR)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            # Write frame
            out.write(frame)
            
            # Control FPS
            elapsed = time.time() - last_time
            sleep_time = (1.0 / self.fps) - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
            last_time = time.time()
            
        out.release()
        self.logger.info(f"Stopped video recording. Video saved to: {filepath}")

    def start(self, name_prefix="automation"):
        """Starts the recording in a separate thread."""
        if self.recording:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name_prefix}_{timestamp}.mp4"
        self.recording = True
        self.thread = threading.Thread(target=self._record, args=(filename,))
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """Stops the recording."""
        self.recording = False
        if self.thread:
            self.thread.join()
            self.thread = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
