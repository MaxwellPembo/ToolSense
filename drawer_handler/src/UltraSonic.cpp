/**************************************************
* FILE: UltraSonic.cpp
* DESC: Handles ultrasonic sensor setup and data
*       retrieval
*
* ENGINEER: Max Pembo
* ------------------------------------------------
* University of Nebraska - Lincoln 
* School of Computing 
* CSCE 438 - Internet of Things 
**************************************************/
#include <WiFi.h>

#include <Arduino.h>
#include "UltraSonic.h"


void ultrasonicSetup(int trigPin, int echoPin){
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  Serial.println("Ultrasonic Setup Complete");
}

// ---------- Function to read an ultrasonic distance ----------
float readUltrasonic(int trigPin, int echoPin) {
    digitalWrite(trigPin, LOW);
    delayMicroseconds(5);

    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);

    long duration = pulseIn(echoPin, HIGH, 30000); // 30 ms timeout

    // Convert to cm (speed of sound = 0.0343 cm/us)
    float distance = duration * 0.0343 / 2;

    if (duration == 0) return -1;  // no reading
    return distance;
}

bool getUlrasonicStatus(int trigPin, int echoPin){
    const int samples = 2;
    float readings[samples];

    // Take multiple readings
    for (int i = 0; i < samples; i++) {
        readings[i] = readUltrasonic(trigPin, echoPin);
        delay(20); // small gap to reduce interference
    }

    for (int i = 0; i < samples - 1; i++) {
        for (int j = i + 1; j < samples; j++) {
            if (readings[j] < readings[i]) {
                float tmp = readings[i];
                readings[i] = readings[j];
                readings[j] = tmp;
            }
        }
    }

    float medianDistance = readings[samples / 2];

    // If no reading, keep previous stable state
    if (medianDistance < 0) return false;

    // Determine OPEN/CLOSED
    return medianDistance > 10;

}
