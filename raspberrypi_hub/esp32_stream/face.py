"""*************************************************
FILE: face.py  

DESC: Handles face detection and facial recognition
      this library depends on a data folder

ENGINEERS: Carter Fogle

REQUIREMENTS: TODO add more requirements here

************************************************* 
University of Nebraska - Lincoln 
School of Computing 
CSCE 438 - Internet of Things 
*************************************************"""

import cv2
import os
import face_recognition
from .toolsense_utils import determine_platform
import numpy as np
from PIL import Image, ExifTags


class FaceDetector:
    """Detects faces using OpenCV Haar cascades, optimized for Pi with downscaling."""

    def __init__(self, cascade_path=None, downscale=0.5,padding=10):
        """
        downscale: float, scale factor for faster detection (0.5 = half size)
        """
        self.downscale = downscale
        self.padding = padding
        sys_platform = determine_platform()
        if cascade_path is None:
            if sys_platform == "raspberry_pi":
                cascade_path = "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"
            else:
                cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        if self.face_cascade.empty():
            raise RuntimeError(f"[FaceDetector] Failed to load cascade at: {cascade_path}")

    def detect(self, frame):
        """
        Detect faces and return a list of dicts: {"bbox": (x, y, w, h), "embedding": np.array}
        """
        small_frame = cv2.resize(frame, (0, 0), fx=self.downscale, fy=self.downscale)
        gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
        boxes = self.face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)

        # Scale boxes back
        scaled_boxes = [(int(x / self.downscale), int(y / self.downscale),
                        int(w / self.downscale), int(h / self.downscale)) for (x, y, w, h) in boxes]

        results = []
        rgb_frame = frame[:, :, ::-1].copy()  # BGR -> RGB

        locations = face_recognition.face_locations(rgb_frame)
        results = []
        if not locations:
            return results
        
        encodings = face_recognition.face_encodings(rgb_frame,locations)
        
        for loc,enc in zip(locations, encodings):
            top,right,bottom,left = loc
            bbox = (left,top,right - left, bottom - top)
            results.append({"bbox":bbox,"embedding":enc})
        

        return results

