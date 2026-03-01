#### Complete the code accordingly ####
import paho.mqtt.client as mqtt
import os
import json
import mysql.connector
import time
from datetime import datetime

# --- Environment Variables ---
MARIADB_HOST = str(os.environ.get("MARIADB_HOST"))
MARIADB_USER = str(os.environ.get("MARIADB_USER"))
MARIADB_PASSWORD = str(os.environ.get("MARIADB_PASSWORD"))
MARIADB_DATABASE = str(os.environ.get("MARIADB_DATABASE"))
MQTT_BROKER = str(os.environ.get("MQTT_BROKER"))

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

            print("\nAlert Logger connected to MariaDB.")
            return conn
        except mysql.connector.Error as err:
            print(f"\nFailed to connect to DB: {err}. Retrying in 5 seconds...")
            time.sleep(5)

def create_alerts_table(cursor):
    try:
        # Complete connector execute
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            device_id VARCHAR(100),
            alert_message VARCHAR(50),
            value FLOAT,
            timestamp DATETIME
        )
        """)
        print("\n'alerts' table ensured to exist.")
    except mysql.connector.Error as err:
        print(f"\nFailed to create 'alerts' table: {err}")

# --- MQTT Callbacks ---
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("\nAlert Logger connected to RabbitMQ.")
        client.subscribe("/sic/alerts/#")
        print("\nSubscribed to /sic/alerts/#")
    else:
        print(f"\nFailed to connect, return code {reason_code}\n")

def on_message(client, userdata, msg):
    global db_connection
    try:
        payload = json.loads(msg.payload.decode())
        print(f"\nAlert received: {payload}")
        
        # Convert ISO string to a datetime object ---
        timestamp_str = payload.get('timestamp')
        if timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str)
        else:
            timestamp = datetime.now()
        
        # Store the alert in the database
        cursor = db_connection.cursor()
        sql = """
        INSERT INTO alerts (device_id, alert_message, value, timestamp)
        VALUES (%s, %s, %s, %s)
        """
        # Use the new datetime object in the query
        val = (
            payload['device_id'],
            payload['alert_message'],
            payload['value'],
            timestamp
        )
        cursor.execute(sql, val)
        db_connection.commit()
        print(f"\nAlert from {payload['device_id']} stored in the database.")
        cursor.close()

    except Exception as e:
        print(f"\nAn error occurred: {e}")

# --- Main Logic ---
if __name__ == '__main__':
    print("\nStarting Alert Logger...")
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    create_alerts_table(db_cursor)
    db_cursor.close()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    
    client.connect(MQTT_BROKER, 1883, 60)
    client.loop_forever()
