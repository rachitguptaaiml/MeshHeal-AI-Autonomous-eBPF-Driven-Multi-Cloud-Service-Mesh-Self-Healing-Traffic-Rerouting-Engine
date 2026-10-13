import subprocess
import requests
import random
import time
import json
SERVICES = ["inventory", "payments", "orders", "auth", "gateway"]

def set_degradation(service, level):
    command = f'docker compose exec {service} wget -qO- --post-data="{{\\"level\\":{level}}}" --header="Content-Type: application/json" http://localhost:4000/set-degradation'
    subprocess.run(command, shell=True)