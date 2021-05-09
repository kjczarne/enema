from dataclasses import dataclass
from datetime import datetime
from flask_restful import Resource


@dataclass
class SubsystemInfo:
    subsystem_id: int  # PK
    node_id: int
    subsystem_kind: int
    description: str
    is_busy: bool

    def get(self):
        return self.__dict__, 200


@dataclass
class SubsystemsTable:
    subsystems: SubsystemInfo

    def get(self):
        return self.__dict__, 200


@dataclass
class CongestionResolverEvent:
    event_id: int  # PK
    subsystem_id: int  # FK
    start: datetime
    finish: datetime


@dataclass
class ScheduleTable:
    events: CongestionResolverEvent


class SubsystemsRoute(Resource):
    
    def get(self):
        return SubsystemInfo(0, 0, 0, "lol", True).get()


class ScheduleRoute(Resource):
    pass