from paho.mqtt import client as mqtt_client
import time
import threading

from schema.aggregated_data_schema import AggregatedDataSchema
from schema.parking_schema import ParkingSchema
from file_datasource import FileDatasource
import config


def connect_mqtt(broker, port):
    print(f"CONNECT TO {broker}:{port}")

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to MQTT Broker ({broker}:{port})!")
        else:
            print(f"Failed to connect {broker}:{port}, return code {rc}")
            exit(rc)

    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.connect(broker, port)
    client.loop_start()
    return client


def publish_agent(client, topic, datasource, delay):
    while True:
        time.sleep(delay)
        data = datasource.read()
        msg = AggregatedDataSchema().dumps(data)
        client.publish(topic, msg)


def publish_parking(client, topic, datasource, delay):
    while True:
        time.sleep(delay)
        parking_data = datasource.readParking()
        msg = ParkingSchema().dumps(parking_data)
        print(f"Send parking `{msg}` to topic `{topic}`")
        print(f"Send agent `{msg}` to topic `{topic}`")
        client.publish(topic, msg)


def run():
    client = connect_mqtt(config.MQTT_BROKER_HOST, config.MQTT_BROKER_PORT)

    datasource = FileDatasource(
        "data/accelerometer.csv",
        "data/gps.csv",
        "data/parking.csv"
    )

    datasource.startReading()

    threading.Thread(
        target=publish_agent,
        args=(client, "agent_data_topic", datasource, config.DELAY),
        daemon=True
    ).start()

    threading.Thread(
        target=publish_parking,
        args=(client, "parking_data_topic", datasource, config.DELAY),
        daemon=True
    ).start()

    while True:
        time.sleep(1)


if __name__ == "__main__":
    run()
