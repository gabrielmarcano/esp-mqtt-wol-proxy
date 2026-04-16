# ESP32 MQTT Wake-on-LAN (WoL) Proxy

A dedicated hardware proxy built with an ESP32 and MicroPython to securely wake up local infrastructure (like an Ubuntu home server and a cloud gaming server) from outside the local network, completely bypassing CGNAT restrictions.

## Architecture

This project solves the issue of sending Magic Packets from the internet to a local network behind a strict CGNAT firewall. Instead of exposing ports, the ESP32 maintains a persistent outbound MQTT connection.

**The Workflow:**
1. **Telegram:** User sends a command (`/wake_server` or `/wake_rog`) to a custom Telegram Bot.
2. **n8n (Self-Hosted):** An n8n instance receives the webhook, verifies the Telegram User ID for security, and publishes a message to a cloud MQTT broker.
3. **HiveMQ Cloud:** Acts as the serverless MQTT broker bridging the external network and the local network.
4. **ESP32 (This Repo):** Listens via TLS-encrypted MQTT. Upon receiving the payload, it crafts a UDP Broadcast Magic Packet and wakes up the targeted machine physically.

## Hardware Requirements

* 1x ESP32 Development Board (ESP32 is required over ESP8266 due to RAM requirements for TLS handshakes).
* 5V Power Supply (e.g., standard wall charger or router USB port).
* Target machines configured to accept Wake-on-LAN in their BIOS/UEFI and OS settings (Ethernet connection highly recommended).

## Software & Deployment

### 1. ESP32 Setup
* Flash your ESP32 with the latest [MicroPython firmware](http://micropython.org/download/esp32/).
* Install the `umqtt.simple` library on your board if it's not included in your specific firmware build.

### 2. Environment Variables
To prevent credential leaks, this repository ignores the `secrets.py` file.
1. Clone the repository.
2. Rename `secrets.example.py` to `secrets.py`.
3. Add your Wi-Fi credentials, HiveMQ Cluster URL, MQTT user/password, and target MAC addresses.
4. Upload both `main.py` and your configured `secrets.py` to the root of your ESP32 using Thonny, ampy, or your preferred IDE.

### 3. Usage
Once powered on, the ESP32 will automatically:
1. Connect to the specified Wi-Fi network.
2. Establish a secure TLS connection with the HiveMQ broker.
3. Subscribe to the command topic.
4. Wait for the `ubuntu` or `gaming` payload to dispatch the broadcast packet.

## Security Notice
* **Never commit `secrets.py` to source control.**
* Ensure your n8n or automation backend filters incoming requests by your specific User ID to prevent unauthorized wake commands.

