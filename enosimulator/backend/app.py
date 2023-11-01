import logging
import os
import sqlite3
from time import time
from typing import Dict

from flask import Flask, request
from flask_restful import Api, Resource
from setup import Setup
from simulation import Simulation
from tenacity import retry, stop_after_attempt


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
            with FlaskApp.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM vminfo WHERE name = ? AND datetime(measuretime) > datetime('now', '-30 minutes') ORDER BY measuretime DESC",
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
            "netrx",
            "nettx",
        ]
        if any(field not in data for field in required_fields):
            return {"message": "Missing field"}, 400

        FlaskApp.db_insert_values("vminfo", data)
        return {"message": "VM info updated successfully"}, 200

    @classmethod
    def create_api(cls):
        return cls


class VMList(Resource):
    def get(self):
        return self.response

    @classmethod
    def create_api(cls, response):
        cls.response = response
        return cls


class Containers(Resource):
    def get(self):
        container_name = request.args.get("name")

        if container_name:
            with FlaskApp.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM containerinfo WHERE name = ? AND datetime(measuretime) > datetime('now', '-30 minutes') ORDER BY measuretime DESC",
                    (container_name,),
                )
                container_infos = cursor.fetchall()

                response = [dict(container_info) for container_info in container_infos]
                return response
        else:
            return {"message": "Missing container name"}, 400

    def post(self):
        data = request.get_json()
        if not data:
            return {"message": "Invalid JSON"}, 400

        required_fields = [
            "name",
            "cpuusage",
            "ramusage",
            "netrx",
            "nettx",
        ]
        if any(field not in data for field in required_fields):
            return {"message": "Missing field"}, 400

        FlaskApp.db_insert_values("containerinfo", data)
        return {"message": "Container info updated successfully"}, 200

    @classmethod
    def create_api(cls):
        return cls


class ContainerList(Resource):
    def get(self):
        with FlaskApp.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT name FROM containerinfo")
            container_names = cursor.fetchall()

            return [row[0] for row in container_names]

    @classmethod
    def create_api(cls):
        return cls


class RoundInfo(Resource):
    def get(self):
        with self.round_info_lock:
            return {
                "round_id": self.simulation.round_id,
                "remaining_rounds": self.simulation.remaining_rounds,
                "round_duration": round(time() - self.simulation.round_start, 2),
                "round_length": self.simulation.round_length,
                "total_rounds": self.simulation.total_rounds,
            }

    @classmethod
    def create_api(cls, simulation, round_info_lock):
        cls.simulation = simulation
        cls.round_info_lock = round_info_lock
        return cls


class FlaskApp:
    def __init__(self, setup: Setup, simulation: Simulation, locks: Dict):
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
        VmListApi = VMList.create_api(list(self.setup.ips.public_ip_addresses.keys()))
        ContainerApi = Containers.create_api()
        ContainerListApi = ContainerList.create_api()
        RoundInfoApi = RoundInfo.create_api(self.simulation, self.locks["round_info"])
        self.api.add_resource(TeamApi, "/teams")
        self.api.add_resource(ServiceApi, "/services")
        self.api.add_resource(VmApi, "/vminfo")
        self.api.add_resource(VmListApi, "/vmlist")
        self.api.add_resource(ContainerApi, "/containerinfo")
        self.api.add_resource(ContainerListApi, "/containerlist")
        self.api.add_resource(RoundInfoApi, "/roundinfo")

    def run(self) -> None:
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)
        self.app.run(host="0.0.0.0", debug=False)

    def init_db(self) -> None:
        connection = sqlite3.connect("database.db")

        with open(f"{self.path}/schema.sql") as f:
            connection.executescript(f.read())

        connection.commit()
        connection.close()

    @staticmethod
    def get_db_connection() -> sqlite3.Connection:
        connection = sqlite3.connect("database.db")
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    @retry(stop=stop_after_attempt(10))
    def db_insert_values(table_name, data) -> None:
        value_names = ",".join(data.keys())
        value_placeholders = ",".join(["?" for _ in data.keys()])
        with FlaskApp.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"INSERT INTO {table_name}({value_names}) VALUES ({value_placeholders})",
                (tuple([value for value in data.values()])),
            )
            conn.commit()

    def delete_db(self) -> None:
        if os.path.exists("database.db"):
            os.remove("database.db")

    def __del__(self):
        self.delete_db()
