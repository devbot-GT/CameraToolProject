#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 13:46:59 2023

@author: devbot
"""

import RPi.GPIO as GPIO
import sys

# GPIO pin number for the LED ring light
LED_PIN = 2

# Initialize the GPIO settings
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

# Create a PWM object for controlling the LED brightness
pwm_led = GPIO.PWM(LED_PIN, 300)  # Pin 2, frequency 300 Hz

# Start the PWM with an initial duty cycle of 0 (LEDs off)
pwm_led.start(0)

# Function to set the brightness of the LED ring light
def set_brightness(brightness):
    # Map the brightness value (0-100) to the PWM duty cycle (0-100)
    duty_cycle = (brightness / 100) * 100
    pwm_led.ChangeDutyCycle(duty_cycle)

# Function to clean up GPIO resources
def cleanup_gpio():
    pwm_led.stop()
    GPIO.cleanup()

# Main loop to continuously listen for brightness updates
try:
    while True:
        # Read the command from the SSH terminal
        command = sys.stdin.readline().strip()

        if command == 'off':
            # Terminate the script
            cleanup_gpio()
            break

        try:
            brightness = int(command)
            set_brightness(brightness)
        except ValueError:
            pass

except KeyboardInterrupt:
    # Clean up GPIO resources when the script is interrupted
    cleanup_gpio()