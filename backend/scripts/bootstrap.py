from influxdb import InfluxDBClient
import requests
import json
import sys


def configure_lightowl(admin_password: str, ip_address: str, lightowl_token: str):
    form: dict = {
        "username": "admin",
        "password": admin_password,
        "confirm_password": admin_password,
        "ip_address": ip_address,
        "lightowl_token": lightowl_token
    } 

    response = requests.post(
        "http://127.0.0.1:8000/api/v1/auth/install",
        data=json.dumps(form),
        headers={"Content-Type": "application/json"}
    )

    response.raise_for_status()
    print(f"User admin successfully configured")

def configure_influxdb():
    print("Configuring InfluxDB")
    client = InfluxDBClient(host="influxdb")
    client.create_database("lightowl")

    # Create Retention Policy. Default to 1 week
    client.create_retention_policy("lightowl_retention_policy", "1w", "1", database="lightowl", default=True)


if __name__ == "__main__":
    admin_password: str = sys.argv[1]
    ip_address: str = sys.argv[2]
    lightowl_token: str = sys.argv[3]

    configure_lightowl(admin_password, ip_address, lightowl_token)
    configure_influxdb()
