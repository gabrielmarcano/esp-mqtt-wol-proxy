import network
import socket
import time
import machine
import ssl
from umqtt.simple import MQTTClient

# Securely import credentials
import secrets 


# Get device MAC as text
import machine
import ubinascii

mac_id = ubinascii.hexlify(machine.unique_id()).decode('utf-8')

# Unique ID: 'esp32_wol_a1b2c3d4e5f6'
MQTT_CLIENT_ID = f'esp32_wol_{mac_id}'
MQTT_PORT      = 8883

def wake_on_lan(mac_address):
    try:
        # Clean the MAC address and convert to bytes
        mac_clean = mac_address.replace(':', '').replace('-', '')
        if len(mac_clean) != 12:
            print("Invalid MAC address format")
            return
            
        mac_bytes = bytes.fromhex(mac_clean)
        
        # Build the Magic Packet: 6 bytes of FF + 16 repetitions of the MAC
        magic_packet = b'\xff' * 6 + mac_bytes * 16
        
        # Create UDP socket and send via Broadcast
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(magic_packet, ('255.255.255.255', 9))
        s.close()
        print(f"[*] Magic Packet dispatched to {mac_address}")
        
    except Exception as e:
        print(f"Error dispatching WoL: {e}")

def mqtt_callback(topic, msg):
    print(f"Message received on {topic}: {msg}")
    
    # Decode the byte message to string
    command = msg.decode('utf-8').lower()
    
    if command == 'ubuntu':
        print("Initiating WoL sequence for Ubuntu Server...")
        wake_on_lan(secrets.MAC_UBUNTU)
    elif command == 'gaming':
        print("Initiating WoL sequence for Cloud Gaming Server...")
        wake_on_lan(secrets.MAC_GAMING)
    else:
        print("Unknown command ignored.")

def main():
    # 1. Connect to Wi-Fi
    print("Connecting to Wi-Fi...")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASS)
    
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(1)
    print(f"\n[+] Wi-Fi Connected. IP: {wlan.ifconfig()[0]}")

    # 2. Connect to HiveMQ (with SSL/TLS)
    print("Connecting to HiveMQ Cluster...")
    client = MQTTClient(
        client_id=MQTT_CLIENT_ID,
        server=secrets.MQTT_BROKER,
        port=MQTT_PORT,
        user=secrets.MQTT_USER,
        password=secrets.MQTT_PASSWORD,
        keepalive=60,
        ssl=True,
        ssl_params={'server_hostname': secrets.MQTT_BROKER}
    )
    
    client.set_callback(mqtt_callback)
    
    try:
        client.connect()
        client.subscribe(secrets.MQTT_TOPIC)
        print(f"[+] Connected and subscribed to: {secrets.MQTT_TOPIC.decode('utf-8')}")
        
        # 3. Listen indefinitely
        while True:
            # check_msg() processes incoming messages without entirely blocking the CPU
            client.check_msg()
            time.sleep(0.5) 
            
    except Exception as e:
        print(f"MQTT Connection Error: {e}")
        time.sleep(5)
        # Auto-recover by resetting the board if connection drops
        machine.reset() 

if __name__ == '__main__':
    main()

