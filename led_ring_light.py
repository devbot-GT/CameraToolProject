#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 13:46:59 2023

@author: devbot
"""

from gpiozero import PWMLED, DigitalOutputDevice
import sys

# GPIO pin numbers
POWER_PIN = 2
PWM_PIN = 12

# Set up GPIO pin 2 as an output
power = DigitalOutputDevice(POWER_PIN)

# Set up PWM on GPIO pin 12 with a frequency of 120 Hz
pwm_led = PWMLED(PWM_PIN, frequency=120)

# Function to set the brightness of the LED ring light
def set_brightness(brightness):
    # Map the brightness value (0-100) to the PWM value (0-1)
    pwm_led.value = brightness / 100

def start_ring_light(brightness):
    # Set the initial brightness of the LED and turn on
    set_brightness(brightness)
    # Main loop to continuously listen for brightness updates
    try:
        while True:
            # Read the command from the SSH terminal
            command = sys.stdin.readline().strip()
    
            if command == 'off':
                # Terminate the script
                break
    
            try:
                brightness = int(command)
                set_brightness(brightness)
            except ValueError:
                pass
    
    except KeyboardInterrupt:
        pass

# Get brightness from arg and illuminate the ring light
brightness = int(sys.argv[1])
start_ring_light(brightness)

# Clean up resources
pwm_led.close()
power.close()
