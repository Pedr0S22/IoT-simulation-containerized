#### Complete the code accordingly ####


import paho.mqtt.client as mqtt
import os
import json
import mysql.connector
import time
from datetime import datetime, timezone

# --- Environment Variables ---
MARIADB_USER = str(os.environ.get("MARIADB_USER"))
MARIADB_PASSWORD = str(os.environ.get("MARIADB_PASSWORD"))
MARIADB_DATABASE = str(os.environ.get("MARIADB_DATABASE"))
MARIADB_HOST = str(os.environ.get("MARIADB_HOST"))
TEMP_HTHRESHOLD = float(os.environ.get("TEMP_HTHRESHOLD"))
TEMP_LTHRESHOLD = float(os.environ.get("TEMP_LTHRESHOLD"))

# --- Database Connection ---
def get_db_connection():
    while True:
        try:
            conn = mysql.connector.connect(
                host=MARIADB_HOST,
                user=MARIADB_USER,
                password=MARIADB_PASSWORD,
                database=MARIADB_DATABASE
            )
            print("\nMetric Processor connected to MariaDB.")
            return conn
        except mysql.connector.Error as err:
            print(f"\nFailed to connect to DB: {err}. Retrying in 5 seconds...")
            time.sleep(5)

def create_metrics_table(cursor):
    try:
        # Create table if not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INT AUTO_INCREMENT PRIMARY KEY,
            device_id VARCHAR(50),
            metric_type VARCHAR(50),
            value FLOAT,
            timestamp DATETIME
        )
        """)
        print("\n'metrics' table ensured to exist.")
    except mysql.connector.Error as err:
        print(f"\nFailed to create 'metrics' table: {err}")

# --- MQTT Callbacks ---
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("\nMetric Processor connected to RabbitMQ.")
        client.subscribe("/sic/metrics/#")
        print("\nSubscribed to /sic/metrics/#")
    else:
        print(f"\nFailed to connect, return code {reason_code}\n")

def on_message(client, userdata, msg):
    global db_connection
    try:
        payload = json.loads(msg.payload.decode())
        print(f"\nMessage received on topic {msg.topic}: {payload}")
        
        # Convert ISO string to datetime object ---
        timestamp = datetime.fromisoformat(payload['timestamp'])
        
        # Store every metric in the database
        cursor = db_connection.cursor()
        sql = """
        INSERT INTO metrics (device_id, metric_type, value, timestamp)
        VALUES (%s, %s, %s, %s)
        """
        # Use the new datetime object in the query
        val = (payload['device_id'], payload['metric_type'], payload['value'], timestamp)
        cursor.execute(sql, val)
        db_connection.commit()
        print(f"\nMetric from {payload['device_id']} stored in the database.")
        cursor.close()

        # Anomaly Detection Logic
        if payload['metric_type'] == 'temperature':
            if payload['value'] > TEMP_HTHRESHOLD:
                print(f"\nHigh temp Anomaly detected! {payload['value']} > exceeds threshold {TEMP_HTHRESHOLD}.")

                alert_message = {
                    "device_id": payload['device_id'],
                    "alert_message": f"High temperature detected: {payload['value']}ºC",
                    "value": payload['value'],
                    "timestamp": datetime.now(timezone.utc).isoformat(), 
                }

                # Publish the alert message to the MQTT broker
                client.publish("/sic/alerts", json.dumps(alert_message))
                print(f"\nHigh temp Alert published: {alert_message}")
            elif payload['value'] < TEMP_LTHRESHOLD:
                print(f"\nLow temp Anomaly detected! {payload['value']} < below threshold {TEMP_LTHRESHOLD}.")
                alert_message = {
                    "device_id": payload['device_id'],
                    "alert_message": f"Low temperature detected: {payload['value']}ºC",
                    "value": payload['value'],
                    "timestamp": datetime.now(timezone.utc).isoformat(), 
                    }
                client.publish("/sic/alerts", json.dumps(alert_message))
                print(f"\nLow temp Alert published: {alert_message}")

    except Exception as e:
        print(f"\nAn error occurred: {e}")

# --- Main Logic ---
if __name__ == '__main__':
    print("\nStarting Metric Processor...")
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    create_metrics_table(db_cursor)
    db_cursor.close()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("rabbitmq", 1883, 60)
    client.loop_forever()
