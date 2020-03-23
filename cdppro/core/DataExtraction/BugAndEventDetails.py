import os
import time
from datetime import datetime

import pandas as pd

from Parser.Json.BugsJsonParser import BugsJsonParser
from Parser.Json.EventsJsonParser import EventsJsonParser
from Utility.CDPConfigValues import CDPConfigValues
from Utility.Utilities import Utilities
from WebConnection.WebConnection import WebConnection


class BugAndEventDetails:
    """Fetches Bug and Events data for a particular branch and prepare the respective csv files after parsing
       1. get_bug_data - Get all Bug details asynchronously
       2. get_event_data - Get all events details asynchronously
    	3. get_events_data_for_scheduler - Get all events details asynchronously when running code through scheduler
    """

    def __init__(self, web_constants, project):
        """
        Class Constructor
        
        :param web_connection: Object of web connection class
        :type web_connection: object
        :param web_constants: object of web_constants class. It contains constant details like different github URLs about any project.
        :type web_constants: Object
        :param bug_url: github bug url
        :type bug_url: str
        :param event_url: github event url
        :type event_url: str
        :param bug_data_frame: Pandas dataframe used for bugs data collection
        :type bug_data_frame: Pandas dataframe
        :param event_data_frame: Pandas dataframe used for bugs data collection 
        :type event_data_frame: Pandas dataframe
        :param project: unique project id of the project for which data is to be collected
        :type project: str
        :param project_name: project name of the project for which data is to be collected
        :type project_name: str
        :param cdp_dump_path: path of directory where bugs data will be saved
        :type cdp_dump_path: str
        :param closed_bug_data_frame: Pandas dataframe used for storing data about bugs that have been closed
        :type closed_bug_data_frame: Pandas dataframe
        """
        self.web_connection = WebConnection()
        self.web_constants = web_constants
        self.bug_url = web_constants.bug_url
        self.event_url = web_constants.event_url
        self.bug_data_frame = None
        self.event_data_frame = None
        self.project = project
        self.project_name = CDPConfigValues.configFetcher.get('name', project)
        self.cdp_dump_path = f"{CDPConfigValues.cdp_dump_path}/{self.project_name}"
        CDPConfigValues.create_directory(self.cdp_dump_path)
        self.closed_bug_data_frame = ""

    def get_bug_data(self, current_date=None):
        """ 
        get_bug_data, internal method used for getting bugs data for a project.
		
        :param current_date : Today's date. Defaults to none
        :type current_date : date
        :returns: Pandas Dataframe that contains bugs data.
        :rtype: Pandas Dataframe
        """
        start_time = time.time()
        bug_data = self.web_connection.get_async_data_using_asyncio_paginated(self.bug_url, self.web_constants, 5)
        end_time = time.time()
        # print(f"Commit data using Parallel (asyncio)\n {commit_data}\n\n")
        print(f"Time Taken to Fetch Bug Details {end_time - start_time}")
		
        bugs_parser = BugsJsonParser()
        bug_list_df = bugs_parser.parse_json(bug_data)

        if current_date is None:
            current_date = datetime.today().strftime('%Y-%m-%d')
            directory = f"{CDPConfigValues.schedule_file_path}/{self.project_name}/{current_date}"
            CDPConfigValues.create_directory(directory)
            bug_list_df.to_csv(
                f"{CDPConfigValues.schedule_file_path}/{self.project_name}/{current_date}/"
                f"{CDPConfigValues.project_issue_list_file_name}",
                index=False)
        else:
            bug_list_df.to_csv(f"{self.cdp_dump_path}/{CDPConfigValues.project_issue_list_file_name}", index=False)

        return bug_list_df

    def get_event_data(self, ):
        """
        internal method used for getting list of events for closed bugs.
        
        """
        
        if os.path.exists(f"{self.cdp_dump_path}/{CDPConfigValues.project_issue_list_file_name}"):
            self.bug_data_frame = pd.read_csv(f"{self.cdp_dump_path}/{CDPConfigValues.project_issue_list_file_name}")
        else:
            self.bug_data_frame = self.get_bug_data()
        self.closed_bug_data_frame = self.bug_data_frame[self.bug_data_frame['STATE'] == 'closed']
        self.closed_bug_data_frame = self.closed_bug_data_frame.reset_index()

        self.event_data_frame = self.closed_bug_data_frame[["ISSUE_ID", "CREATED_TIMESTAMP", "UPDATED_TIMESTAMP"]]

        """Fetch the Bug Id's from the data frame"""
        list_of_issues = self.closed_bug_data_frame['ISSUE_ID'].tolist()

        """using the Bugs Id list create event url list"""
        url_list = Utilities.format_url(self.event_url, list_of_issues)
        start_time = time.time()

        results = self.web_connection.get_async_data_using_asyncio(url_list, self.web_constants,
                                                                   batch_size=CDPConfigValues.git_api_batch_size)

        list_of_buggy_commits = results[0]
        failed_urls = results[1]
        loop_counter = 1

        while len(failed_urls) > 0:
            time.sleep(60 * loop_counter)
            print(f"Total Failed URL's re-trying {len(failed_urls)}")
            results = self.web_connection.get_async_data_using_asyncio(failed_urls, self.web_constants,
                                                                       batch_size=CDPConfigValues.git_api_batch_size // 2)
            failed_urls = results[1]
            list_of_buggy_commits = list_of_buggy_commits + results[0]
        end_time = time.time()
        print("Parallel time taken to get all event data using (asyncio) =", end_time - start_time)

        list_of_buggy_commits = pd.DataFrame(list_of_buggy_commits, columns=["ISSUE_ID", "JSON_RESPONSE"])
        list_of_buggy_commits['ISSUE_ID'] = list_of_buggy_commits['ISSUE_ID'].astype(str)
        self.event_data_frame['ISSUE_ID'] = self.event_data_frame['ISSUE_ID'].astype(str)
        self.event_data_frame = pd.merge(self.event_data_frame, list_of_buggy_commits, how="left",
                                         left_on=["ISSUE_ID"],
                                         right_on=["ISSUE_ID"])

        self.event_data_frame.to_csv(f"{self.cdp_dump_path}/github_events_cdp_dump.csv", encoding='utf-8-sig',
                                     index=False)
        event_parser = EventsJsonParser()
        event_parser.find_buggy_commits_based_on_repository_fixes(self.web_constants, self.event_data_frame,
                                                                  f"{self.cdp_dump_path}/"
                                                                  f"{CDPConfigValues.closed_events_list_file_name}")

    def get_events_data_for_scheduler(self, current_date, previous_bug_df, previous_closed_events_df):
        """
        internal method used for getting list of events for closed bugs.
        
        :param current_date: Today's date
        :type current_date: date
        :param previous_bug_df: Dataframe of bugs file that is created from get_bug_data function
        :type previous_bug_df: Pandas Dataframe
        :param previous_closed_events_df: Dataframe containing details of closed bugs with fix commit ids
        :type previous_closed_events_df: Pandas Dataframe
        :returns: event dataframe for latest events for bugs that happened after previous_bug_df
        :rtype: Pandas Dataframe
        """
        self.bug_data_frame = self.get_bug_data()
        self.closed_bug_data_frame = self.bug_data_frame[self.bug_data_frame['STATE'] == 'closed']

        self.closed_bug_data_frame = self.closed_bug_data_frame.reset_index()

        self.closed_bug_data_frame = self.closed_bug_data_frame[
            ~(self.closed_bug_data_frame.ISSUE_ID.isin(previous_bug_df.ISSUE_ID))]

        if len(self.closed_bug_data_frame) != 0:
            self.event_data_frame = self.closed_bug_data_frame[["ISSUE_ID", "CREATED_TIMESTAMP", "UPDATED_TIMESTAMP"]]

            """Fetch the Bug Id's from the data frame"""
            list_of_issues = self.closed_bug_data_frame['ISSUE_ID'].tolist()

            """using the Bugs Id list create event url list"""
            url_list = Utilities.format_url(self.event_url, list_of_issues)
            start_time = time.time()

            results = self.web_connection.get_async_data_using_asyncio(url_list, self.web_constants,
                                                                       batch_size=CDPConfigValues.git_api_batch_size)

            list_of_buggy_commits = results[0]
            failed_urls = results[1]
            loop_counter = 1

            while len(failed_urls) > 0:
                time.sleep(60 * loop_counter)
                print(f"Total Failed URL's re-trying {len(failed_urls)}")
                results = self.web_connection.get_async_data_using_asyncio(failed_urls, self.web_constants,
                                                                           CDPConfigValues.git_api_batch_size // 2)
                failed_urls = results[1]
                list_of_buggy_commits = list_of_buggy_commits + results[0]

            end_time = time.time()
            print("Parallel time taken to get all event data using (asyncio) =", end_time - start_time)

            list_of_buggy_commits = pd.DataFrame(list_of_buggy_commits, columns=["ISSUE_ID", "JSON_RESPONSE"])
            list_of_buggy_commits['ISSUE_ID'] = list_of_buggy_commits['ISSUE_ID'].astype(str)
            self.event_data_frame['ISSUE_ID'] = self.event_data_frame['ISSUE_ID'].astype(str)
            self.event_data_frame = pd.merge(self.event_data_frame, list_of_buggy_commits, how="left",
                                             left_on=["ISSUE_ID"],
                                             right_on=["ISSUE_ID"])

            self.event_data_frame.to_csv(
                f"{CDPConfigValues.schedule_file_path}/{self.project_name}/{current_date}/github_events_cdp_dump.csv",
                encoding='utf-8-sig', index=False)
            event_parser = EventsJsonParser()
            event_df = event_parser.find_buggy_commits_based_on_repository_fixes(self.web_constants,
                                                                                 self.event_data_frame)

            event_df = pd.concat([event_df, previous_closed_events_df], ignore_index=True)

            return event_df

        else:
            return None
