from flask import Flask
from flask_restful import Api, Resource
from .data_model import (SubsystemsTable, ScheduleTable, 
                         CongestionResolverEvent, SubsystemInfo,
                         SubsystemsRoute, ScheduleRoute)

flask_app = Flask(__name__)
api = Api(flask_app)

api.add_resource(SubsystemsRoute, '/status')
api.add_resource(ScheduleRoute, '/schedule')
