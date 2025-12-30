/**************************************************
* FILE: main.cpp
* DESC: ESP32 - Drawer handler main file
*
* ENGINEER: Max Pembo
* ------------------------------------------------
* University of Nebraska - Lincoln 
* School of Computing 
* CSCE 438 - Internet of Things 
**************************************************/
#include <WiFi.h>
#include <esp_wifi.h>
#include <lwip/def.h>
#include "UltraSonic.h"
 
// WIFI
// const char* ssid = "NU-IoT";
// const char* password = "rlqpqrlz";
// const char* ssid = "Verizon_6K79QT";
// const char* password = "mobile-via6-fry";
const char* ssid     = "carters_iphone_hotspot";
const char* password = "thisisanIoThotspot67$";
 
IPAddress HUB_IP(172,20,10,2);
const int PORT = 5002;
 
WiFiClient client;
 
//  Ultrasonic Pins
// Sensor 1
#define TRIG1 4
#define ECHO1 5
// Sensor 2
#define TRIG2 16
#define ECHO2 17
// Sensor 3
#define TRIG3 18
#define ECHO3 19
 
//  Drawer Status
bool drawer1OpenPrev;
bool drawer2OpenPrev;
bool drawer3OpenPrev;
 
//Function Declarations
bool sendMessage(String& msg);
bool startConnection();
 
void setup() {
  Serial.begin(115200);
  delay(2000);
 
  //Connect to Wifi
  WiFi.begin(ssid, password);
  Serial.println("Connecting...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(300);
    Serial.print(".");
  }
  Serial.println("\nConnected to Wi-Fi");
 
  if (!startConnection()){
    Serial.println("Failed to connect to hub");
    return;
  }
 
  //Setup Ultrasonic Sensors
  ultrasonicSetup(TRIG1, ECHO1);
  ultrasonicSetup(TRIG2, ECHO2);
  ultrasonicSetup(TRIG3, ECHO3);
  Serial.println("\nSetup Complete");
 
  drawer1OpenPrev = getUlrasonicStatus(TRIG1, ECHO1);
  drawer2OpenPrev = getUlrasonicStatus(TRIG2, ECHO2);
  drawer3OpenPrev = getUlrasonicStatus(TRIG3, ECHO3);
}
 
 
void loop() {
    // CHECK FOR CHANGES
    bool d1 = getUlrasonicStatus(TRIG1, ECHO1);
    delay(50);
    if (d1 != drawer1OpenPrev) {
        String msg = String("{\"drawer\":1,\"status\":\"") + (d1 ? "OPEN" : "CLOSED") + "\"}";
        // Send the message to the hub
        sendMessage(msg);
        Serial.println(msg);
        drawer1OpenPrev = d1;  
    }
 
    bool d2 = getUlrasonicStatus(TRIG2, ECHO2);
    delay(50);
    if (d2 != drawer2OpenPrev) {
        String msg = String("{\"drawer\":2,\"status\":\"") + (d2 ? "OPEN" : "CLOSED") + "\"}";
        // Send the message to the hub
        sendMessage(msg);
        Serial.println(msg);
        drawer2OpenPrev = d2;
    }
 
    bool d3 = getUlrasonicStatus(TRIG3, ECHO3);
    delay(10);
    if (d3 != drawer3OpenPrev) {
        String msg = String("{\"drawer\":3,\"status\":\"") + (d3 ? "OPEN" : "CLOSED") + "\"}";
        // Send the message to the hub
        sendMessage(msg);
        Serial.println(msg);
        drawer3OpenPrev = d3;
    }
}
 
 
bool startConnection() {
 
    if (!client.connect(HUB_IP, PORT)) {
        Serial.println("Connection to hub failed");
        return false;
    }
    Serial.println("Connected to hub");
    
    return true;
}
 
 
bool sendMessage(String& msg) {
 
    if (!client.connected()) {
        Serial.println("Client not connected");
        return false;
    }
 
    uint32_t len = msg.length();
    uint32_t net_len = htonl(len);   // BIG endian
 
    // Send length header
    client.write((uint8_t*)&net_len, 4);
 
    // Send JSON payload
    client.write((const uint8_t*)msg.c_str(), len);
 
    Serial.print("SENT: ");
    Serial.println(msg);
 
    return true;
 
}
 