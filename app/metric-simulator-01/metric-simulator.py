#### Complete the code accordingly ####

import paho.mqtt.client as mqtt
import os
import time
import json
import random
from datetime import datetime, timezone

# --- Configuration ---
NUM_MESSAGES = int(os.environ.get("NUM_MESSAGES"))
N_TEMP_HIGH = float(os.environ.get("N_TEMP_HIGH"))
N_TEMP_LOW = float(os.environ.get("N_TEMP_LOW"))
A_TEMP_HIGH = float(os.environ.get("A_TEMP_HIGH"))
A_TEMP_LOW = float(os.environ.get("A_TEMP_LOW"))
A_PROBA = float(os.environ.get("A_PROBA"))
DEVICE_ID = "device_01"

# --- MQTT Callbacks ---
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("\nMetric Simulator connected to RabbitMQ")
    else:
        print(f"\nFailed to connect, return code {reason_code}\n")

def on_publish(client, userdata, mid, reason_code, properties):
    print(f"\nMessage {mid} published.")

def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    print(f"\nDisconnected with result code: {reason_code}")

# --- Main Logic ---
if __name__ == '__main__':
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish
    print("Starting Metric Simulator...")
    connected = False
    while not connected:
        try:
            print("\nTrying to connect to the broker...")
            client.connect("rabbitmq", 1883, 60)
            connected = True
        except ConnectionRefusedError:
            print("\nConnection refused. Retrying in 5 seconds...")
            time.sleep(5)
            
    client.loop_start()

    # Generate messages
    for i in range(NUM_MESSAGES):
        # Generate a normal temperature reading
        temperature = random.uniform(N_TEMP_LOW, N_TEMP_HIGH)

        # Decide if anomaly occurs
        if random.random() < A_PROBA:
            if random.random() < 0.5:
                # High anomaly
                temperature = random.uniform(A_TEMP_HIGH, A_TEMP_HIGH + 10)
            else:
                # Low anomaly
                temperature = random.uniform(A_TEMP_LOW - 10, A_TEMP_LOW)

        
        payload = {
            "device_id": DEVICE_ID,
            "metric_type": "temperature",
            "value": round(temperature, 2),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        topic = "/sic/metrics/temperature"
        print(f"\nPublishing to {topic}: {payload}")
        # Publish the message
        client.publish(topic, json.dumps(payload))
        # Wait for 2 seconds before sending the next message
        time.sleep(2)

    print("\nMetric Simulator finished publishing.")
    client.loop_stop()
    client.disconnect()
