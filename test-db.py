import requests

test_data = {
    "name": "test",
    "status": "test",
    "uptime": "test",
    "cpuusage": 2.3,
    "ramusage": 31.2,
    "netusage": 43.2,
}

r = requests.post("http://localhost:5000/vminfo", json=test_data)
print(r.content)
