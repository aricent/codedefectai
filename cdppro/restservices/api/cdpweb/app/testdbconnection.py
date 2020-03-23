from django.db import connections
from django.db.utils import OperationalError
from django.http import JsonResponse


class TestDbConnecton:
    def __init__(self,):
        pass

    def check(self,server):

        db_conn = connections[server]
        try:
            c = db_conn.cursor()
        except OperationalError:
            connected = False
        else:
            connected = True

        return connected

    def get_db_server(self):
        testdbconnection = TestDbConnecton()
        flag = testdbconnection.check("default")
        db_server = "default"
        if flag != True:
            flag = testdbconnection.check("replica")
            db_server = "replica"
            if flag != True:
                return JsonResponse({"response" : "Server is temporarily down !!!"})

        return db_server