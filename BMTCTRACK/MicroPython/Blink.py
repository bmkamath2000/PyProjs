import time
from machine import Pin

# Most ESP32 dev boards have a built-in LED on GPIO pin 2
led = Pin(2, Pin.OUT)

print("Starting ESP32 Blink Program...")

while True:
    led.value(1)     # Turn the LED on
    time.sleep(0.5)  # Wait for 0.5 seconds
    led.value(0)     # Turn the LED off
    time.sleep(0.5)  # Wait for 0.5 seconds
