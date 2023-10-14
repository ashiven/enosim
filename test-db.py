import requests

test_data = {
    "name": "test2",
    "status": "test",
    "uptime": "test",
    "cpuusage": "test",
    "ramusage": "test",
    "netusage": "test",
    "measuretime": "test",
}

r = requests.post("http://localhost:5000/vminfo", json=test_data)
print(r.content)
