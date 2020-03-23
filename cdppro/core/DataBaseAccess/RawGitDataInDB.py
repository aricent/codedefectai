import json
import traceback
from datetime import datetime

import pandas as pd

from DataBaseAccess.MariaDB import MariaDB
from Utility.CDPConfigValues import CDPConfigValues


class RawGitDataInDB:
    """
        Class used to fetch gitdata of a project and saved it into DB.
	"""

    def __init__(self, project):
        self.project = project
        self.project_name = CDPConfigValues.configFetcher.get("name", project)
        self.friendly_name = CDPConfigValues.configFetcher.get("friendly_name", project)
        self.maria_db = None
        self.project_id = None
        self.current_date = None

    def get_maria_db_connection(self):
        """
            Method used to establish DB connection.
		"""
		
        if self.maria_db is None or self.maria_db.conn is None or not self.maria_db.conn.is_connected():
            self.maria_db = MariaDB(host=CDPConfigValues.host, port=CDPConfigValues.port,
                                    database=CDPConfigValues.database,
                                    user_name=CDPConfigValues.username, password=CDPConfigValues.password)

    def get_number_of_days_to_fetch_data(self):
        """
            Util method.
		"""

        global days
        self.get_maria_db_connection()
        try:
            query = f"Select * From predictionrawdata Inner Join projects On projects.Id  = " \
                f"predictionrawdata.ProjectId Where projects.ProjectName = '{self.friendly_name}' "
            print(f"Get Number of Days to Fetch Data : {query}")
            cursor = self.maria_db.execute_query(query)

            if cursor.rowcount <= 0:
                days = 30
            else:
                days = 1

            self.maria_db.close_connection()
        except Exception as e:
            print("Exception occurred....Closing database connections....")
            print(e)
            traceback.print_tb()
            self.maria_db.close_connection()

        return days

    def get_project_id(self):
        """
            Util method to get project ID.
		"""

        if self.project_id is None:
            self.get_maria_db_connection()
            query = f"select id from projects where ProjectName = '{self.friendly_name}'"
            print(f"Get Project Id : {query}")
            try:
                cursor = self.maria_db.execute_query(query)
                self.project_id = cursor.fetchall()[0][0]
                self.maria_db.close_connection()
                return self.project_id
            except Exception as e:
                print("Exception occurred....Closing database connections....")
                traceback.print_tb()
                print(e)
                self.maria_db.close_connection()
        else:
            return self.project_id

    def check_current_day_execution(self, date):
        """
            Util method to check the execution of particular date.
            
            :param date: Date whose execution is checked.
            :type date: datetime
        """
        self.get_maria_db_connection()
        query = f"select count(Day) from predictionrawdata where Day = '{date}' and ProjectId = {self.project_id}"
        print(f"Check Current Day Execution : {query}")
        day_count = 0
        try:

            cursor = self.maria_db.execute_query(query)
            day_count = cursor.fetchall()[0][0]

        except Exception as e:
            print("Check Current Day Execution :: Exception occurred....Closing database connections....")
            print(f"Exception Occurred!!!")
            traceback.print_tb()
            self.maria_db.close_connection()

        self.maria_db.close_connection()

        if day_count == 0:
            return True

        return False

    def insert_commit_details_to_db(self, dataframe, project_id):
        """
            Method used to save gitdata in to DB.
		
    		:param dataframe: Dataframe which contains gitdata needs to be inserted in to DB.
			:type dataframe: DataFrame
            
            :param project_id: Project ID whose data to be inserted.
            :type project_id: str
		"""

        self.current_date = datetime.today().strftime('%Y-%m-%d')

        if self.check_current_day_execution(self.current_date):

            self.get_maria_db_connection()
            print(f"Inserting Commit Data for project Id {project_id}")

            try:
                query = """Insert Into `predictionrawdata`(`DAY`, `ProjectId`, `RAW_DATA`) Values(%s, %s, %s) """
                print(f"Insert Commit Details :: {query}")
                value_tuple = (self.current_date, project_id, dataframe.to_json())
                print(f"value tuple :: {value_tuple}")
                self.maria_db.insert_query(query, value_tuple)
                print("Query executed")
            except Exception as e:
                print("Insert Commit Details to DB :: Exception occurred....Closing database connections....")
                #print(f"Exception Occurred!!!\n{traceback.print_exc()}")
                print(e)
                self.maria_db.close_connection()

        else:
            print(f" Data is already inserted in PredictionRawData table for Date {self.current_date}")

    def fetch_commit_data(self, date=None):
        """
            Method used to fetch the commit details.
		"""
        self.get_maria_db_connection()
        if date is not None:
            self.current_date = date
        data_frame = pd.DataFrame()
        try:
            query = f"select RAW_DATA from predictionrawdata where projectId = {self.project_id} and DAY = '{self.current_date}'"
            print(f"Fetch Commit Query : {query}")
            cursor = self.maria_db.execute_query(query)
            raw_data = cursor.fetchall()

            for data in raw_data:
                print(f"Json List Len {len(data)}")
                for json_string in data:
                    json_data = json.loads(json_string)
                    data_frame = pd.concat([data_frame, pd.DataFrame.from_records(json_data)], ignore_index=True)

            self.maria_db.close_connection()

        except Exception as e:
            print("Exception occurred....Closing database connections....")
            traceback.print_tb()
            print(e)
            self.maria_db.close_connection()

        return data_frame


if __name__ == "__main__":
    git_data = RawGitDataInDB("project_1")
    git_data.get_maria_db_connection()
    git_data.get_project_id()
    git_data.fetch_commit_data()
