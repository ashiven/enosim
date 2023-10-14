from time import sleep

import requests

test_data = {
    "name": "test",
    "status": "test",
    "uptime": "test",
    "cpuusage": 2.3,
    "ramusage": 31.2,
    "netusage": 43.2,
}

for _ in range(20):
    r = requests.post("http://localhost:5000/vminfo", json=test_data)
    print(r.content)
    sleep(1)
