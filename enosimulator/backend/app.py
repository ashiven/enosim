import logging
import threading

from flask import Flask
from flask_restful import Api, Resource


class Teams(Resource):
    def get(self):
        with threading.Lock():
            response = {name: team.to_json() for name, team in self.teams.items()}
            return response

    @classmethod
    def create_api(cls, teams):
        cls.teams = teams
        return cls


class Services(Resource):
    def get(self):
        with threading.Lock():
            response = {
                name: service.to_json() for name, service in self.services.items()
            }
            return response

    @classmethod
    def create_api(cls, services):
        cls.services = services
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
    def __init__(self, setup, simulation):
        self.app = Flask(__name__)
        self.setup = setup
        self.simulation = simulation

        # Create RESTful API endpoints
        self.api = Api(self.app)
        ServiceApi = Services.create_api(self.setup.services)
        TeamApi = Teams.create_api(self.setup.teams)
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
