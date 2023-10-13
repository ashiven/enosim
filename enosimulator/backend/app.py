import logging

from flask import Flask
from flask_restful import Api, Resource


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
        return self.response

    @classmethod
    def create_api(cls, response):
        cls.response = response
        return cls


class VMHistory(Resource):
    def get(self):
        return self.response

    @classmethod
    def create_api(cls, response):
        cls.response = response
        return cls


class FlaskApp:
    def __init__(self, setup, simulation, locks):
        self.app = Flask(__name__)
        self.setup = setup
        self.simulation = simulation
        self.locks = locks

        # Create RESTful API endpoints
        self.api = Api(self.app)
        ServiceApi = Services.create_api(self.setup.services, self.locks["service"])
        TeamApi = Teams.create_api(self.setup.teams, self.locks["team"])
        self.api.add_resource(TeamApi, "/teams")
        self.api.add_resource(ServiceApi, "/services")

        # TODO:
        # - there will be sync issues with the main thread
        # - figure out how to make this work

        # VmApi = VMs.create_api(self.setup.vms)
        # VmHistoryApi = VMHistory.create_api(self.setup.vm_history)
        # self.api.add_resource(VmApi, "/vminfo")
        # self.api.add_resource(VmHistoryApi, "/vmhistory")

    def run(self):
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)
        self.app.run(debug=False)
