from dataclasses import dataclass
from datetime import datetime
from flask_restful import Resource
from flask import request
from typing import ClassVar
from pathlib import Path
from enema.crypto import decrypt_password, KEY

import os
import sqlite3
import pandas as pd


root = Path(os.path.dirname(__file__))


db_connection = lambda: sqlite3.connect(root / 'app.db')

read_table = lambda table: pd.read_sql_query(
    f"SELECT * FROM {table}", 
    db_connection()
)

get_rows = lambda df: [row.to_dict() for _, row in df.iterrows()]

@dataclass
class Tables:
    nodes: ClassVar[str] = "nodes"
    subsystems: ClassVar[str] = "subsystems"
    schedules: ClassVar[str] = "schedules"
    auth: ClassVar[str] = "auth"
    api_auth: ClassVar[str] = "api_auth"


update_status = lambda val, id: db_connection().executescript(
    f"UPDATE {Tables.subsystems} SET is_busy = {val} WHERE subsystem_id = {id}"
)

get_joined_nodes_and_subsystems = lambda: pd.read_sql_query(f"""
select * from {Tables.subsystems}
left join {Tables.nodes} 
ON {Tables.subsystems}.node_id = {Tables.nodes}.node_id;
""", db_connection())

get_auth_header = lambda: request.headers.get('Authorization')


def with_auth(response, auth_header):
    """Returns a valid API response if the Authorization
    header with Basic token has been provided. Otherwise
    returns 401 Unauthorized response."""
    if auth_header:
        for _, row in read_table(Tables.api_auth).iterrows():
            decrypted = decrypt_password(row['token'], KEY)
            auth_header.replace("Basic ", "") == decrypted
        return response, 200
    return {'message': 'unauthorized!'}, 401


class SubsystemsRoute(Resource):
    
    def get(self):
        """Gets all subsystem as a list of rows from the table"""
        resp = get_joined_nodes_and_subsystems().to_dict('records')
        return with_auth(resp, get_auth_header())
    
    def post(self):
        """Adds new subsystem into the table"""
        pass

    def put(self):
        """Updates existing subsystem in the table"""
        pass
        # TODO: sub-route that handles status update (/subsystem/{id}/status)

    def delete(self):
        """Removes a subsystem from the table"""
        pass


class NodesRoute(Resource):

    def get(self):
        """Gets the nodes table as a list of rows"""
        resp = read_table(Tables.nodes).to_dict('records')
        return with_auth(resp, get_auth_header())
    
    def post(self):
        """Adds new node into the table"""
        pass

    def put(self):
        """Updates existing node in the table"""
        pass

    def delete(self):
        """Removes a node from the table"""
        pass
