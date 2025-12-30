/**************************************************
* FILE: main.cpp
* DESC: ESP32-CAM main file for communication
*       with Raspberry Pi hub.
*
* ENGINEER: Carter Fogle
* ------------------------------------------------
* University of Nebraska - Lincoln 
* School of Computing 
* CSCE 438 - Internet of Things 
**************************************************/

#include "esp_camera.h"
#include <WiFi.h>
#include <ESP32Ping.h>
#include <WiFiUdp.h>

// --- NETWORK SELECTION ---
#define HOTSPOT
// #define SCHOOL_NETWORK

// --- WiFi Credentials ---
#ifdef HOME_NETWORK
const char* ssid     = "totally_not_an_IoT_network";
const char* password = "@mb2a:))!QE$";
#endif

#ifdef SCHOOL_NETWORK
const char* ssid     = "NU-IoT";
const char* password = "ntxshnbs";
#endif

#ifdef HOTSPOT
const char* ssid     = "carters_iphone_hotspot";
const char* password = "thisisanIoThotspot67$";

// const char* ssid     = "totally_not_an_IoT_network";
// const char* password = "@mb2a:))!QE$";
#endif

IPAddress HUB_IP(192,168,1,178);
const int PORT = 5001;

void startCamera() {
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;

    config.pin_d0 = 5;
    config.pin_d1 = 18;
    config.pin_d2 = 19;
    config.pin_d3 = 21;
    config.pin_d4 = 36;
    config.pin_d5 = 39;
    config.pin_d6 = 34;
    config.pin_d7 = 35;

    config.pin_xclk  = 0;
    config.pin_pclk  = 22;
    config.pin_vsync = 25;
    config.pin_href  = 23;
    config.pin_sccb_sda = 26;
    config.pin_sccb_scl = 27;
    config.pin_pwdn = 32;
    config.pin_reset = -1;

    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;
    config.frame_size = FRAMESIZE_VGA;
    config.jpeg_quality = 12;
    config.fb_count = 2;

    if (esp_camera_init(&config) != ESP_OK) {
        Serial.println("Camera init failed");
        while (true);
    }
}

// UDP Hub discovery on client - client enabled networks
IPAddress discover_hub() {
    WiFiUDP udp;
    udp.begin(4210);

    unsigned long lastSend = 0;

    Serial.println("Starting auto-discovery…");

    while (true) {
        unsigned long now = millis();

        // Broadcast every second
        if (now - lastSend > 1000) {
            udp.beginPacket("255.255.255.255", 4210);
            udp.print("ESP32_DISCOVERY_CAM");
            udp.endPacket();
            lastSend = now;
            Serial.println("Broadcast sent.");
        }

        int packetSize = udp.parsePacket();
        if (packetSize) {
            char buf[50];
            int len = udp.read(buf, sizeof(buf) - 1);
            buf[len] = '\0';

            Serial.printf("Received: %s\n", buf);

            if (String(buf).startsWith("HUB_ACK")) {
                IPAddress ip = udp.remoteIP();
                Serial.printf("Hub found at: %s\n", ip.toString().c_str());
                return ip;
            }
        }
    }
}

// ========== SERIAL IP INPUT ==========
String readLine() {
    String s = "";
    while (true) {
        if (Serial.available()) {
            char c = Serial.read();
            if (c == '\n' || c == '\r') break;
            s += c;
        }
    }
    return s;
}

// ========== SETUP ==========
void setup() {
    Serial.begin(115200);
    delay(2000);
    Serial.print("ESP MAC: ");
    Serial.println(WiFi.macAddress());
    Serial.println("\nConnecting to WiFi…");
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        Serial.print(".");
        delay(500);
    }

    Serial.printf("\nConnected! IP: %s\n", WiFi.localIP().toString().c_str());

#ifdef HOTSPOT
    Serial.println("Enter Raspberry Pi IP address:");
    String ipStr = readLine();

    if (!HUB_IP.fromString(ipStr)) {
        Serial.println("Invalid IP format. Aborting.");
        while (true);
    }

    Serial.printf("Using HUB IP: %s\n", HUB_IP.toString().c_str());
#else
    // HUB_IP = discover_hub();
#endif
    Serial.print("Pinging hub...");
    if (Ping.ping(HUB_IP) >= 0) {
        Serial.println("Reachable!");
    } else {
        Serial.println("UNREACHABLE!");
    }
    // flash LED PWM
    ledcSetup(0,5000,8);
    ledcAttachPin(4,0);
    ledcWrite(0, 6);

    startCamera();
}

void loop() {
    WiFiClient client;

    if (!client.connect(HUB_IP, PORT)) {
        Serial.println("Failed to connect to hub.");
        delay(1000);
        return;
    }

    Serial.println("Connected. Streaming…");

    while (client.connected()) {
        camera_fb_t *fb = esp_camera_fb_get();
        if (!fb) continue;

        uint32_t len = fb->len;
        client.write((uint8_t*)&len, 4);
        client.write(fb->buf, fb->len);

        esp_camera_fb_return(fb);
        delay(50);
    }

    client.stop();
}