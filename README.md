How to Stream ADS-B Aircraft Data from Raspberry Pi to MQTT for Node-RED
Overview
This guide shows you how to decode ADS-B aircraft signals on a Raspberry Pi Zero 2W with an RTL-SDR dongle, then stream decoded aircraft data to a remote MQTT broker for use with Node-RED or other home automation systems.

Prerequisites
Raspberry Pi Zero 2W with RTL-SDR installed and running readsb

MQTT broker running on your network (e.g., on IP 10.10.50.8, standard port 1883)

Python3 installed on the Pi

Network connectivity between Pi and MQTT broker

Step 1: Verify readsb is running and outputting JSON data
Make sure your readsb service includes the option:

css
Copy
Edit
--net-json-port 30154
Check the service status:

bash
Copy
Edit
sudo systemctl status readsb
Verify it listens on port 30154:

bash
Copy
Edit
sudo netstat -tlnp | grep 30154
You should see output like:

nginx
Copy
Edit
tcp   0   0 0.0.0.0:30154   0.0.0.0:*   LISTEN   <pid>/readsb
Test the JSON stream:

bash
Copy
Edit
printf "GET /data/aircraft.json\r\n\r\n" | nc localhost 30154
You should see many JSON objects, each representing one aircraft, printed line by line.

Step 2: Understand the JSON stream format
The JSON data is a stream of individual JSON objects separated by newlines, not a single JSON array.

Your code must parse the stream line by line.

Step 3: Create the ADS-B to MQTT Python bridge script
Save the following as /usr/local/bin/adsb-to-mqtt.py:

python
Copy
Edit
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
Make executable:

bash
Copy
Edit
sudo chmod +x /usr/local/bin/adsb-to-mqtt.py
Test manually:

bash
Copy
Edit
python3 /usr/local/bin/adsb-to-mqtt.py
You should see aircraft data publishing messages in the console.

Step 4: Install paho-mqtt system-wide
Ensure the MQTT Python client library is installed globally:

bash
Copy
Edit
sudo pip3 install --upgrade --force-reinstall paho-mqtt
Verify it’s installed in a system-wide path (not root-only):

bash
Copy
Edit
python3 -m pip show paho-mqtt
Step 5: Create a systemd service to run the script at boot
Create the service file:

bash
Copy
Edit
sudo nano /etc/systemd/system/adsb-mqtt.service
Paste:

ini
Copy
Edit
[Unit]
Description=ADSB to MQTT Bridge
After=network.target

[Service]
ExecStart=/usr/bin/python3 /usr/local/bin/adsb-to-mqtt.py
Restart=always
User=pi
WorkingDirectory=/home/pi
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=adsb-mqtt

[Install]
WantedBy=multi-user.target
Adjust User=pi and WorkingDirectory as needed.

Reload systemd and enable the service:

bash
Copy
Edit
sudo systemctl daemon-reload
sudo systemctl enable adsb-mqtt.service
sudo systemctl start adsb-mqtt.service
Check status and logs:

bash
Copy
Edit
sudo systemctl status adsb-mqtt.service
sudo journalctl -f -u adsb-mqtt.service
Troubleshooting summary
No JSON data: Ensure readsb is running with --net-json-port 30154.

No aircraft decoded: Check RTL-SDR hardware, location, and gain settings.

Python module not found in systemd: Install paho-mqtt globally with sudo pip3 install.

Service fails repeatedly: Check logs with journalctl for errors, adjust Python environment or permissions.

Final notes
The script publishes each aircraft as an individual JSON message to the MQTT topic adsb/aircraft.

You can consume this topic in Node-RED with MQTT-in nodes to build dashboards, alerts, or other automations.

Customize the script and MQTT topic as needed for your setup.
