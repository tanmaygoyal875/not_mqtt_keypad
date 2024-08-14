
import network
import time
from machine import Pin
import ujson
from umqtt.simple import MQTTClient

# MQTT Server Parameters
MQTT_CLIENT_ID = "micropython-keypad-demo"
MQTT_BROKER    = "broker.mqttdashboard.com"
MQTT_USER      = ""
MQTT_PASSWORD  = ""
MQTT_TOPIC     = "wokwi-keypad"

# Keypad configuration
ROWS = [13, 12, 14, 27]  # Connect to the keypad row pins
COLS = [26, 25, 33, 32]  # Connect to the keypad column pins
KEYS = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

class Keypad:
    def __init__(self, keys, row_pins, col_pins):
        self.keys = keys
        self.row_pins = [Pin(pin, Pin.OUT) for pin in row_pins]
        self.col_pins = [Pin(pin, Pin.IN, Pin.PULL_UP) for pin in col_pins]
    
    def get_key(self):
        for i, row_pin in enumerate(self.row_pins):
            row_pin.value(0)
            for j, col_pin in enumerate(self.col_pins):
                if not col_pin.value():
                    row_pin.value(1)
                    return self.keys[i][j]
            row_pin.value(1)
        return None

keypad = Keypad(KEYS, ROWS, COLS)

print("Connecting to WiFi", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Wokwi-GUEST', '')
while not sta_if.isconnected():
    print(".", end="")
    time.sleep(0.1)
print(" Connected!")

print("Connecting to MQTT server... ", end="")
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)
client.connect()

print("Connected!")

while True:
    key = keypad.get_key()
    if key:
        message = ujson.dumps({"key": key})
        print(f"Key pressed: {key}")
        print(f"Reporting to MQTT topic {MQTT_TOPIC}: {message}")
        client.publish(MQTT_TOPIC, message)
    time.sleep(0.1)
