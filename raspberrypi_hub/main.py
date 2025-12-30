"""
*************************************************
FILE: main.py  

DESC: Hub handler for Toolbox Hub. Handles:
      - ESP32 cam discovery or direct connection
      - Face detection + recognition
      - Optional displayed video stream

ENGINEERS: Carter Fogle

*************************************************
University of Nebraska - Lincoln 
School of Computing 
CSCE 438 - Internet of Things 
*************************************************
"""

import cv2
import socket
import fcntl
import struct
import netifaces
import json
from esp32_stream import ESP32Stream, FaceDetector
from azure.iot.device import IoTHubDeviceClient,Message
import numpy as np
import time
import select
import threading


# =====================================================
#              CONFIGURATION
# =====================================================

HOME_NETWORK = False
SCHOOL_NETWORK = True      # <<< SET THIS

DISCOVERY_PORT = 4210      # Broadcast network
SERVER_PORT = 5001         # ESP32 will connect to this

CONNECTION_STRING = "HostName=ToolSense.azure-devices.net;DeviceId=toolsense-hub3;SharedAccessKey=2FUWisiamzlI6KnDf1ev4a8ByYo5OQrTkJVZtjOz6bc="

DEBUG = False


def get_wifi_ip():
    for iface in ["wlan0", "wlan1", "wlp2s0"]:
        try:
            addrs = netifaces.ifaddresses(iface)
            return addrs[netifaces.AF_INET][0]["addr"]
        except:
            pass
    return None

do_video = True if input(
    "Display video? (needs graphics support, hint check echo $DISPLAY)\nY/n: "
) == "Y" else False


def is_use_last_user(embedding: np.ndarray) -> bool:
    return embedding.ndim == 1 and embedding.size == 1 and embedding[0] == 0

def discover_esp_home_network():
    print("[HUB] Starting ESP broadcast discovery...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("0.0.0.0", DISCOVERY_PORT))

    while True:
        data, addr = sock.recvfrom(1024)
        msg = data.decode().strip()

        print("[HUB] Received:", msg, "from", addr[0])

        if msg == "ESP32_DISCOVERY_CAM":
            print(f"[HUB] ESP32 CAM discovered at {addr[0]}")
            sock.sendto(b"HUB_ACK", addr)
            return addr[0]

def manual_ip_mode():
    hub_ip = get_wifi_ip()
    print(f"[HUB] Your Raspberry Pi IP is: **{hub_ip}**")
    print("[HUB] Enter this IP on the ESP32 when it asks.\n")
    print("Waiting for ESP32 to connect...\n")
    return hub_ip

def send_toolbox_event(embedding,drawer_state):
    global last_send_time, last_embedding
    payload = {
        "event" : {
            "event_id" : int(time.time() * 1000),
            "face_embedding" : embedding.tolist(),
            "drawer_info" : drawer_state
        }
    }
    
    message = Message(json.dumps(payload))
    client.send_message(message)
    
    last_send_time = time.time()
    last_embedding = np.array(embedding)

    print("Sending embedding to IoT Hub")

if HOME_NETWORK:
    HUB_IP = discover_esp_home_network()
elif SCHOOL_NETWORK:
    HUB_IP = manual_ip_mode()
else:
    raise RuntimeError("No network mode selected.")

client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
try:
    client.connect()
    print("Connected to IoT Hub")
except Exception as e:
    print("Failed to connect to IoT Hub", e)
    
stream = ESP32Stream()
stream.start_server()

detector = FaceDetector()

print("[HUB] Ready. Waiting for frames...\n")

last_send_time = 0

cool_down = 3

last_embedding = None
MIN_EMBEDDING_DIFF = 0.5

stable_counter = 0
STABLE_THRESHOLD = 5

last_drawer_event = None

def drawer_loop():
    global last_drawer_event
    while True:
        event = stream.receive_drawer_event()
        if event:
            if last_drawer_event:
                new_drawer = int(event['drawer'])
                new_status = event['status']
                last_drawer = int(last_drawer_event['drawer'])
                last_status = last_drawer_event['status']
                
                if (new_drawer == last_drawer) and (last_status == "OPEN") and (new_status == "CLOSED") and last_embedding is not None:
                    # Same user closed the drawers
                    send_toolbox_event(last_embedding,event)
                
                        
            last_drawer_event = event
            print("Drawer event:", event)

threading.Thread(target=drawer_loop, daemon=True).start()

while True:
    frame = stream.receive_frame()
    if frame is None:
        continue
    # process frame
    results = detector.detect(frame)

    if do_video:
        for r in results:
            x, y, w, h = r["bbox"]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imshow("Faces", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        if DEBUG:
            print(results)
        
    if len(results) == 0:
        stable_counter = 0
        last_embedding = None
        if DEBUG:
            print("Results empty")
        continue

    stable_counter += 1

    #Skip rest if there is not enough evidence for a face    
    if stable_counter < STABLE_THRESHOLD:
        continue

    face = results[0]
    embedding = face["embedding"]

    #Skip if we are sending too much
    if time.time() - last_send_time < cool_down:
        continue
    
    #check last embedding against new one, don't want to send same data twice
    if (last_embedding is not None):


        if is_use_last_user(last_embedding):
            continue
        dot = np.dot(embedding, last_embedding)
        n1 = np.linalg.norm(embedding)
        n2 = np.linalg.norm(embedding)
        similarity = dot / (n1*n2)
        
        dist = 1 - similarity
        if DEBUG:
            print(dist)
        
        if dist < MIN_EMBEDDING_DIFF:
            #likely same person do not send again
            continue
        
    # If we make it this far safe to send the embedding
    send_toolbox_event(embedding,last_drawer_event)
if do_video:
    cv2.destroyAllWindows()
