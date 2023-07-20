#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 22:12:24 2023

@author: devbot
"""

import signal
from gpiozero import PWMLED, DigitalOutputDevice
import sys

# GPIO pin numbers
POWER_PIN = 2
PWM_PIN = 18

# Set up GPIO pin 2 as an output
power = DigitalOutputDevice(POWER_PIN)

# Set up PWM on GPIO pin 12 with a frequency of 120 Hz
pwm_led = PWMLED(PWM_PIN, frequency=120)

def handle_termination(sig, frame):
    print("\nTerminating the LED ring light script...")
    pwm_led.close()
    power.close()
    exit(0)

# Set up the signal handler
signal.signal(signal.SIGINT, handle_termination)
signal.signal(signal.SIGTERM, handle_termination)

# Get brightness from arg and illuminate the ring light
brightness = sys.argv[1]
if brightness == 'off':
    pwm_led.close()
    power.close()
else:
    brightness = int(brightness)
    # Map the brightness value (0-100) to the PWM value (0-1)
    pwm_led.value = brightness / 100
