"""
*************************************************
FILE: __init__.py  

DESC: Lib setup for face detection and esp32
      stream.

ENGINEERS: Carter Fogle

*************************************************
University of Nebraska - Lincoln 
School of Computing 
CSCE 438 - Internet of Things 
*************************************************
"""

from .stream_handler import ESP32Stream
from .face import FaceDetector
from .toolsense_utils import determine_platform