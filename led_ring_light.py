#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 13:46:59 2023

@author: devbot
"""

from gpiozero import PWMLED
import sys

# GPIO pin number for the PWM signal
PWM_PIN = 12

# Create a PWMLED object for controlling the LED ring light
pwm_led = PWMLED(PWM_PIN, frequency=300)

# Function to set the brightness of the LED ring light
def set_brightness(brightness):
    # Map the brightness value (0-100) to the PWM value (0-1)
    pwm_led.value = brightness / 100

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

# Clean up resources
pwm_led.close()
