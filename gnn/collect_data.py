import subprocess
import requests
import random
import time
import json

SERVICES = ["inventory", "payments", "orders", "auth", "gateway"]

def set_degradation(service, level):
    command = f'docker compose exec {service} wget -qO- --post-data="{{\\"level\\":{level}}}" --header="Content-Type: application/json" http://localhost:4000/set-degradation'
    subprocess.run(command, shell=True)

def collect_one_sample(degraded_service, level):
    requests.post('http://localhost:5000/clear')
    set_degradation(degraded_service, level)
    time.sleep(1)
    requests.post('http://localhost:4000/checkout', json={'item': 'widget-a'})
    response = requests.get('http://localhost:5000/telemetry')
    telemetry = response.json()
    set_degradation(degraded_service, 0)
    sample = {
        'degraded_service': degraded_service,
        'degradation_level': level,
        'telemetry': telemetry,
    }
    return sample