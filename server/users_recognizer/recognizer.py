"""
*************************************************
FILE: recognizer.py  

DESC: Handles loading in faces stored in
        in known_faces library

ENGINEERS: Carter Fogle

*************************************************
University of Nebraska - Lincoln 
School of Computing 
CSCE 438 - Internet of Things 
*************************************************
"""


import os
import face_recognition
from .toolsense_utils import determine_platform
import numpy as np
from PIL import Image, ExifTags

class FaceRecognizer:
    """Recognizes faces using face_recognition library."""

    def __init__(self, known_faces_dir="known_faces"):
        self.known_encodings = []
        self.known_names = []

        if not os.path.exists(known_faces_dir):
            print(f"[FaceRecognizer] Directory '{known_faces_dir}' does not exist. No known faces loaded.")
            return

        for name in os.listdir(known_faces_dir):
            person_dir = os.path.join(known_faces_dir, name)
            if not os.path.isdir(person_dir):
                print(f"Skipping {person_dir}, not a directory")
                continue

            for file in os.listdir(person_dir):
                path = os.path.join(person_dir, file)
                if not file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    print(f"Skipping {path}, not an image")
                    continue

                try:
                    # Load image using PIL to handle EXIF artifacts typically from iphone photos
                    pil_image = Image.open(path)

                    try:
                        for orientation in ExifTags.TAGS.keys():
                            if ExifTags.TAGS[orientation] == 'Orientation':
                                break
                        exif = pil_image._getexif()
                        if exif is not None:
                            orientation_val = exif.get(orientation, 1)
                            if orientation_val == 3:
                                pil_image = pil_image.rotate(180, expand=True)
                            elif orientation_val == 6:
                                pil_image = pil_image.rotate(270, expand=True)
                            elif orientation_val == 8:
                                pil_image = pil_image.rotate(90, expand=True)
                    except Exception:
                        pass  # No EXIF info

                    image_np = np.array(pil_image)

                    # Detect faces first
                    locations = face_recognition.face_locations(image_np)
                    if not locations:
                        print(f"No face found in {file}")
                        continue

                    # Encode the first face found
                    encodings = face_recognition.face_encodings(image_np, locations)
                    self.known_encodings.append(encodings[0])
                    self.known_names.append(name)
                    print(f"Loaded face for '{name}' from {file}")

                except Exception as e:
                    print(f"[FaceRecognizer] Failed to load {path}: {e}")

        print(f"[FaceRecognizer] Loaded {len(self.known_encodings)} known faces.")

    def recognize(self, encoding):

        matches = face_recognition.compare_faces(self.known_encodings, encoding)
        name = "Unknown"
        if True in matches:
            name = self.known_names[matches.index(True)]
            print(name)
            return name
        else:
            print("Person not recognized")
            return None

