import logging
import os
import sqlite3

from flask import Flask, request
from flask_restful import Api, Resource

#### Helpers ####


def _get_db_connection():
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    return connection


#### End Helpers ####


class Teams(Resource):
    def get(self):
        with self.team_lock:
            response = {name: team.to_json() for name, team in self.teams.items()}
            return response

    @classmethod
    def create_api(cls, teams, team_lock):
        cls.teams = teams
        cls.team_lock = team_lock
        return cls


class Services(Resource):
    def get(self):
        with self.service_lock:
            response = {
                name: service.to_json() for name, service in self.services.items()
            }
            return response

    @classmethod
    def create_api(cls, services, service_lock):
        cls.services = services
        cls.service_lock = service_lock
        return cls


class VMs(Resource):
    def get(self):
        vm_name = request.args.get("name")

        if vm_name:
            with _get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM vminfo WHERE name = ? AND measuretime > datetime('now', '-30 minutes') ORDER BY measuretime DESC",
                    (vm_name,),
                )
                vm_infos = cursor.fetchall()

                response = [dict(vm_info) for vm_info in vm_infos]
                return response
        else:
            return {"message": "Missing VM name"}, 400

    def post(self):
        data = request.get_json()
        if not data:
            return {"message": "Invalid JSON"}, 400

        required_fields = [
            "name",
            "ip",
            "cpu",
            "ram",
            "disk",
            "status",
            "uptime",
            "cpuusage",
            "ramusage",
            "netusage",
        ]
        if any(field not in data for field in required_fields):
            return {"message": "Missing field"}, 400

        name = data["name"]
        ip = data["ip"]
        cpu = data["cpu"]
        ram = data["ram"]
        disk = data["disk"]
        status = data["status"]
        uptime = data["uptime"]
        cpuusage = data["cpuusage"]
        ramusage = data["ramusage"]
        netusage = data["netusage"]

        with _get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO vminfo(name, ip, cpu, ram, disk, status, uptime, cpuusage, ramusage, netusage) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    name,
                    ip,
                    cpu,
                    ram,
                    disk,
                    status,
                    uptime,
                    cpuusage,
                    ramusage,
                    netusage,
                ),
            )
            conn.commit()

        return {"message": "VM info updated successfully"}, 200

    @classmethod
    def create_api(cls):
        return cls


class FlaskApp:
    def __init__(self, setup, simulation, locks):
        self.app = Flask(__name__)
        self.setup = setup
        self.simulation = simulation
        self.locks = locks
        self.path = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
        self.init_db()

        # Create RESTful API endpoints
        self.api = Api(self.app)
        ServiceApi = Services.create_api(self.setup.services, self.locks["service"])
        TeamApi = Teams.create_api(self.setup.teams, self.locks["team"])
        VmApi = VMs.create_api()
        self.api.add_resource(TeamApi, "/teams")
        self.api.add_resource(ServiceApi, "/services")
        self.api.add_resource(VmApi, "/vminfo")

    def run(self):
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)
        self.app.run(debug=False)

    def init_db(self):
        connection = sqlite3.connect("database.db")

        with open(f"{self.path}/schema.sql") as f:
            connection.executescript(f.read())

        connection.commit()
        connection.close()

    def delete_db(self):
        if os.path.exists("database.db"):
            os.remove("database.db")

    def __del__(self):
        self.delete_db()
