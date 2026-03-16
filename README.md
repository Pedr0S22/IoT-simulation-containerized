# IoT Microservices Environment Simulation

## Project Description
This project is a distributed system designed to simulate a simple Internet of Things (IoT) environment. The system features services for generating sensor data, processing it to detect anomalies, and logging both the raw data and any generated alerts for auditing purposes. It utilizes Docker and Docker Compose to orchestrate a set of microservices that communicate asynchronously through a message broker. The processed data and alerts are stored in a persistent MariaDB database accessible via phpMyAdmin.

## Table of Contents
- [Project Description](#project-description)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Configuration](#configuration)
- [License](#license)
- [Authors](#authors)

## Project Structure
The architecture relies on network separation, with one network for database communications (`database-network`) and another for the message broker (`broker-network`)[cite: 18, 28, 29]. Services must communicate using their DNS names (e.g., rabbitmq, mariadb), not IP addresses.

![System Architecture](./path/to/Figure1_Architecture.png) 
*(Note: Be sure to save the architecture diagram as an image and update this path).*

### Components
* **Message Broker:** RabbitMQ container handling asynchronous MQTT communication on port 1883.
* **Database:** MariaDB container acting as the persistent storage engine on port 3306. It uses a named volume called `mariadb-data` to store its data.
* **Database GUI:** phpMyAdmin container exposed on port 8080:80.
* **Metric Simulator (`metric-simulator.py`):** A publisher service that simulates IoT devices generating environmental data. It periodically generates metric readings (device_id, metric_type, value, timestamp) as a JSON object [cite: 43] and publishes temperature readings to the `/sic/metrics/temperature` topic. It occasionally generates values exceeding a predefined threshold to simulate anomalies.
* **Metric Processor (`metric-processor.py`):** A subscriber/publisher service that is the core of the system. It subscribes to all metric topics using a wildcard (`/sic/metrics/#`) [cite: 55], inserts data into the `metrics` table, and implements an anomaly detection rule to publish new alert messages to the `/sic/alerts` topic if a temperature threshold is exceeded.
* **Alert Logger (`alert-logger.py`):** A specialized subscriber service responsible only for logging alerts. It subscribes specifically to the `/sic/alerts` topic and inserts the alert data into a separate `alerts` table.

## Database Schema
The MariaDB container should automatically create a database named `sic` upon startup. The Python scripts must create the following tables if they do not already exist[cite: 93]:

* **`metrics` table:** * `id` (INT, PK, AI)
  * `timestamp` (TIMESTAMP)
  * `device_id` (VARCHAR)
  * `metric_type` (VARCHAR)
  * `value` (FLOAT)
* **`alerts` table:**
  * `id` (INT, PK, AI)
  * `timestamp` (TIMESTAMP)
  * `device_id` (VARCHAR)
  * `alert_message` (VARCHAR) [cite: 98]
  * `value` (FLOAT) [cite: 98]

## Configuration
The system's behavior is controlled by environment variables[cite: 48, 49, 50, 51, 61, 62, 69].

### Simulator Variables
* `NUM_MESSAGES`: Controls the number of messages to generate[cite: 48].
* `N_TEMP_HIGH` / `N_TEMP_LOW`: Sets the normal temperature range[cite: 49].
* `A_TEMP_HIGH` / `A_TEMP_LOW`: Sets the anomaly temperature range[cite: 50].
* `A_PROBA`: Configures the probability of an anomaly occurring[cite: 51].

### Processor Variables
* `TEMP_THRESHOLD`: The temperature threshold for generating alerts[cite: 61].

*(Additional necessary data to perform different tasks, e.g., connect to the DB, can also be supplied via environment variables[cite: 62, 69].)*

## License
Distributed under the MIT License.

## Authors
* **[Your Name]** - *Development*
* **[Co-Author Name]** - *Development*
