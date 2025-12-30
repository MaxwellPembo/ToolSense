"""*************************************************
FILE: stream_handler.py  

DESC: Creates a ESP32Stream object to handle
      TCP data coming from ESP. ESP directly
      transmits to hub, and the hub listens for
      this.

ENGINEERS: Carter Fogle

REQUIREMENTS: TODO add more requirements here

************************************************* 
University of Nebraska - Lincoln 
School of Computing 
CSCE 438 - Internet of Things 
*************************************************"""

import socket
import numpy as np
import cv2
import struct
import asyncio
import json

class ESP32Stream:
    def __init__(self, ip='0.0.0.0', port=5001, drawer_port=5002):
        self.TCP_IP = ip
        self.TCP_PORT = port
        self.DRAWER_PORT = drawer_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dsock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.conn = None
        self.dconn = None

    def _recv_exact(self, conn, n):
        data = b''
        while len(data) < n:
            packet = conn.recv(min(n - len(data), 4096))
            if not packet:
                return None
            data += packet
        return data

    def start_server(self):
        
        self.dsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.dsock.bind((self.TCP_IP, self.DRAWER_PORT))
        self.dsock.listen(1)
        print(f"Waiting on drawer handler connection on {self.TCP_IP}:{self.DRAWER_PORT}")
        self.dconn, addr = self.dsock.accept()
        print(f"Connected to ESP32-DrawerHandler at {addr}")
        
        
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.TCP_IP, self.TCP_PORT))
        self.sock.listen(1)
        print(f"Waiting for ESP32 connection on {self.TCP_IP}:{self.TCP_PORT}...")
        self.conn, addr = self.sock.accept()
        print(f"Connected to ESP32-Cam at {addr}")
        


    def receive_drawer_event(self):

        header = self._recv_exact(self.dconn, 4)
        if not header:
            return None

        msg_len = struct.unpack(">I", header)[0]
        payload = self._recv_exact(self.dconn, msg_len)
        if not payload:
            return None

        message = json.loads(payload.decode())
        return message
    
    def receive_frame(self):
    # Read exactly 4 bytes for frame length
        header = b''
        while len(header) < 4:
            chunk = self.conn.recv(4 - len(header))
            if not chunk:
                return None
            header += chunk

        frame_len = int.from_bytes(header, 'little')

        if frame_len <= 0 or frame_len > 60000000:
            print(f"[ERROR] Invalid frame size received: {frame_len}")
            return None

        jpeg_bytes = b''
        while len(jpeg_bytes) < frame_len:
            chunk = self.conn.recv(frame_len - len(jpeg_bytes))
            if not chunk:
                return None
            jpeg_bytes += chunk

        img = cv2.imdecode(np.frombuffer(jpeg_bytes, np.uint8), cv2.IMREAD_COLOR)
        return img

    
