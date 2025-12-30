/**************************************************
* FILE: UltraSonic.h
* DESC: Header for UltraSonic Library:
*       Handles setup and ultrasonic data from
*       a given sensor on an esp32 dev module
*
* ENGINEER: Max Pembo
* ------------------------------------------------
* University of Nebraska - Lincoln 
* School of Computing 
* CSCE 438 - Internet of Things 
**************************************************/

#ifndef ULTRASONIC_H_
#define ULTRASONIC_H_

#include <Arduino.h>

void ultrasonicSetup(int triggerPin, int echoPin);

float readUltrasonic(int trigPin, int echoPin);

bool getUlrasonicStatus(int trigPin, int echoPin);

#endif