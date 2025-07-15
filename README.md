# ADS-B to MQTT Bridge

This project streams ADS-B aircraft data decoded by `readsb` on a Raspberry Pi into an MQTT broker, suitable for use with Node-RED and home automation.

## Setup

1. Ensure `readsb` is installed and running on your Raspberry Pi with JSON output enabled on port 30154.

2. Copy `adsb-to-mqtt.py` to `/usr/local/bin/` and make it executable:

   ```bash
   sudo cp adsb-to-mqtt.py /usr/local/bin/
   sudo chmod +x /usr/local/bin/adsb-to-mqtt.py
   ```

3. Install Python dependencies globally:

   ```bash
   sudo pip3 install --upgrade --force-reinstall paho-mqtt
   ```

4. Copy `adsb-mqtt.service` to `/etc/systemd/system/`:

   ```bash
   sudo cp adsb-mqtt.service /etc/systemd/system/
   ```

5. Reload systemd and enable the service:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable adsb-mqtt.service
   sudo systemctl start adsb-mqtt.service
   ```

6. Check service status and logs:

   ```bash
   sudo systemctl status adsb-mqtt.service
   sudo journalctl -f -u adsb-mqtt.service
   ```

## Configuration

- Edit `adsb-to-mqtt.py` to set your MQTT broker IP, port, and topic as needed.

- Adjust the systemd service file if you use a different user or working directory.

## Troubleshooting

- Make sure `readsb` is outputting JSON data on port 30154.

- Ensure the `paho-mqtt` Python package is installed globally.

- Check firewall/network connectivity to your MQTT broker.

---

Feel free to contribute or open issues!

---
