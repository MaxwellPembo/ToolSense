"""
*************************************************
FILE: server.py  

DESC: Gets messages from IoT Hub and handles
      updating the database file

ENGINEERS: Carter Fogle

*************************************************
University of Nebraska - Lincoln 
School of Computing 
CSCE 438 - Internet of Things 
*************************************************
"""


from azure.eventhub import EventHubConsumerClient
from users_recognizer import FaceRecognizer
import json
import numpy as np
import pandas as pd

CONNECTION_STR = "Endpoint=sb://ihsuprodwestus3res002dednamespace.servicebus.windows.net/;SharedAccessKeyName=iothubowner;SharedAccessKey=UgLhVHFelBBpzfQovv3lxNQXw0qVb/S+AAIoTGFedHc=;EntityPath=iothub-ehub-toolsense-69321081-411ad604a2"
EVENTHUB_NAME = "iothub-ehub-toolsense-69321081-411ad604a2"
CONSUMER_GROUP = "$Default"  
CSV_FILE = "DrawerInfo.csv"

df = pd.read_csv(CSV_FILE)
columns = df.columns.str.strip().to_list()
df.columns = columns

# Global counter so every message gets a unique number
message_counter = 0
recognizer = FaceRecognizer()
last_opened = "none"
 
def is_use_last_user(embedding: np.ndarray) -> bool:
    return embedding.ndim == 1 and embedding.size == 1 and embedding[0] == 0


def on_event(partition_context, event):
    global message_counter, last_opened
    message_counter += 1
    df = pd.read_csv(CSV_FILE)
    # Optional: mark progress
    partition_context.update_checkpoint(event)
    
    j_event = json.loads(event.body_as_str())
    event = j_event["event"]
    
    embedding = np.array(event["face_embedding"])
    drawer_state = event["drawer_info"]
    drawer_num = int(drawer_state["drawer"])
    drawer_status = drawer_state["status"]
    
    
    if is_use_last_user(embedding):
        new_user = last_opened
    else:
        new_user = recognizer.recognize(embedding)
    if not new_user:
        return
    
    print(new_user)
    
    curr_user = df.loc[df['Number'] == drawer_num, 'CurrentUser'].values[0]
    tool_stat = bool(df.loc[df['Number'] == drawer_num, 'Status'].values[0])
    last_user = df.loc[df['Number'] == drawer_num, 'LastUser'].values[0]
    
    if(drawer_status == "CLOSED"):
        open_close = False
        if curr_user == new_user:
            #User put back the tool
            print("first if")
            tool_stat = True
            last_user = curr_user
            curr_user = "none"
        elif (curr_user != new_user) and (tool_stat):
            #new user took tool
            print("second if")
            tool_stat = False
            curr_user = new_user
        elif (curr_user != new_user) and not tool_stat:
            #new user just checked to see if tool is in toolbox
            print("3rd if")
            tool_stat = False
    
    else:
        open_close = True
        last_opened = new_user
        
    df.loc[df['Number'] == drawer_num, ['Status', 'IsOpen', 'CurrentUser', 'LastUser']] = [
         tool_stat, open_close, curr_user , last_user]
    
    print(df)
    
    df.to_csv(CSV_FILE,index=False)
        
 
if __name__ == "__main__":
    client = EventHubConsumerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        consumer_group=CONSUMER_GROUP,
        eventhub_name=EVENTHUB_NAME
    )
    
    print("Listening for messages. Press Ctrl+C to exit.")
    try:
        with client:
            client.receive(
                on_event=on_event,
                starting_position="@latest")
    except KeyboardInterrupt:
        print("Stopped.")