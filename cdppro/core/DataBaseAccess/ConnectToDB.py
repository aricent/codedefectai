from DB.MariaDB import MariaDB
from Utility.CDPConfigValues import CDPConfigValues


class ConnectToDB:
    """
        Class is used to establish and release the DB connection.
    """
    def __init__(self):
        self._maria_db = None

    def connect(self):
        """
            Method used to validate the db connection and create the connection if doesnt exist."
		
    		:return Return the DB connection instance
		"""
        if self._maria_db is None or self._maria_db.conn is None or not self._maria_db.conn.is_connected():
            self._maria_db = MariaDB(host=CDPConfigValues.host, port=CDPConfigValues.port,
                                     database=CDPConfigValues.database,
                                     user_name=CDPConfigValues.username, password=CDPConfigValues.password,
                                     ssl={'ssl': {'ssl-ca': '/cdpscheduler/certificate/BaltimoreCyberTrustRoot.crt.pem'}})
        return self._maria_db

    def close(self):
        """
            Method used to terminate the DB connection.
        """
        self._maria_db.close_connection()
        self.maria_db = None
