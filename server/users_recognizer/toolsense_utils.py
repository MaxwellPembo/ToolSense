"""*************************************************
FILE: utils.py  

DESC: Utility for stream data from esp

ENGINEERS: Carter Fogle

REQUIREMENTS: TODO add more requirements here

************************************************* 
University of Nebraska - Lincoln 
School of Computing 
CSCE 438 - Internet of Things 
*************************************************"""

import platform

def determine_platform():
    
    system = platform.system()
    
    if system == "Linux":
        try:
            with open("/proc/cpuinfo","r") as f:
                cpuinfo = f.read().lower()
            if "raspberry pi" in cpuinfo or "bcm" in cpuinfo:
                return "raspberry_pi"
        except:
            pass
        return "linux"
    
    if system == "Darwin":
        return "mac"
    
    if system == "Windows":
        return "windows"
    
    
    return