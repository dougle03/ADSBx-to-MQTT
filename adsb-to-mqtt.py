#!/usr/bin/env python3
import socket
import json
import time
import paho.mqtt.client as mqtt

MQTT_BROKER = "10.10.50.8"  # Replace with your MQTT broker IP
MQTT_PORT = 1883
MQTT_TOPIC = "adsb/aircraft"

HOST = "localhost"
PORT = 30154

def fetch_and_publish(client):
    try:
        with socket.create_connection((HOST, PORT), timeout=5) as s:
            s.sendall(b"GET /data/aircraft.json\r\n\r\n")
            buffer = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                buffer += chunk
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    if line.strip():
                        try:
                            aircraft = json.loads(line)
                            client.publish(MQTT_TOPIC, json.dumps(aircraft))
                            print(f"Published aircraft: {aircraft.get('hex', 'N/A')} flight: {aircraft.get('flight', 'N/A')}")
                        except json.JSONDecodeError:
                            print("JSON decode error for line:", line)
    except Exception as e:
        print("Error fetching data:", e)

def main():
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    while True:
        fetch_and_publish(client)
        time.sleep(5)

if __name__ == "__main__":
    main()
