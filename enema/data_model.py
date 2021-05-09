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


def read_table(table): 
    """Reads a SQL table into a Pandas DataFrame"""
    return pd.read_sql_query(
        f"SELECT * FROM {table}", 
        db_connection()
    )


@dataclass
class Tables:
    nodes: ClassVar[str] = "nodes"
    subsystems: ClassVar[str] = "subsystems"
    schedules: ClassVar[str] = "schedules"
    auth: ClassVar[str] = "auth"
    api_auth: ClassVar[str] = "api_auth"


def update_table(val, id, table, column, pk_column):
    """Generalized function that updates a record queried
    by a primary key"""
    if type(val) is str:
        val = f"'{val}'"  # SQL string quotes
    db_connection().executescript(
        f"UPDATE {table} SET {column} = {val} WHERE {pk_column} = {id}"
    )


def update_status(val, id):
    """Updates Subsystem status value"""
    update_table(val, id, Tables.subsystems, 'is_busy', 'subsystem_id')


def get_joined_nodes_and_subsystems():
    """Retrieves a left-joined subsystems and nodes table"""
    return pd.read_sql_query(f"""
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


general_bad_request_message = {
    'message': 'bad request, ' + \
               'make sure you send JSON data like {"status": 1} and ' + \
               'that the Content-Type: application/json header is set'
    }, 400


class StatusRoute(Resource):
    
    def get(self):
        """Gets all subsystem as a list of rows from the table"""
        resp = get_joined_nodes_and_subsystems().to_dict('records')
        return with_auth(resp, get_auth_header())
    
    def post(self):
        """#TODO:Adds new subsystem into the table"""
        pass

    def put(self):
        """#TODO:Updates existing subsystem in the table"""
        pass

    def delete(self):
        """#TODO:Removes a subsystem from the table"""
        pass


class SubsystemStatusRoute(Resource):

    def get(self, subsystem_id):
        """Gets a particular subsystem status"""
        df = get_joined_nodes_and_subsystems()
        resp = df[df['subsystem_id'] == int(subsystem_id)]['is_busy']
        resp = list(resp)
        if len(resp) > 0:
            resp = resp[0]
        else:
            return {'message': f'no subsystem with ID {subsystem_id} seems to exist'}, 400
        return with_auth(resp, get_auth_header())

    def post(self, subsystem_id):
        """Sets a particular subsystem status"""
        req = request.json
        print(req)
        if req:
            resp, return_code = with_auth({}, get_auth_header())
            if return_code == 200:
                status = req['status']
                update_status(status, subsystem_id)
                return {'message': f'status successfully set to {status} for subsystem {subsystem_id}'}, 200
            return resp, return_code
        return general_bad_request_message
    
    def put(self, subsystem_id):
        """Sets a particular subsystem status, equivalent to POST"""
        self.post(subsystem_id)


class NodesRoute(Resource):

    def get(self):
        """Gets the nodes table as a list of rows"""
        resp = read_table(Tables.nodes).to_dict('records')
        return with_auth(resp, get_auth_header())
    
    def post(self):
        """#TODO:Adds new node into the table"""
        pass

    def put(self):
        """#TODO:Updates existing node in the table"""
        pass

    def delete(self):
        """#TODO:Removes a node from the table"""
        pass
