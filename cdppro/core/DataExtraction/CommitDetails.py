import os
import time

import pandas as pd

from Parser.Json.CommitsJsonParser import CommitsJsonParser
from Utility.CDPConfigValues import CDPConfigValues
from Utility.Utilities import Utilities
from VersionControl.GitData import GitData
from WebConnection.WebConnection import WebConnection


class CommitDetails:
    """
        Prepare Commit data for the provided project.
        1. Get all commit data asynchronously
        2. Get commit details asynchronously
    
    """

    def __init__(self, web_constants, project):
        """
        Class Constructor
      
        :param web_connection: Object of web connection class
        :type web_connection: object
        :param web_constants: object of web_constants class. It contains constant details like different github URLs about any project.
        :type web_constants: Object
        :param project: unique project id of the project for which data is to be collected
        :type project: str
        :param commit_url: github commit url for specific to a project
        :type commit_url: str
        :param project_name: project name of the project for which data is to be collected
        :type project_name: str
        :param commit_details_url: baseurl for github commit data
        :type commit_details_url: str
        :param commit_details: details fetched for a commit
        :type commit_details: str
        :param cdp_dump_path: path of directory where bugs data will be saved
        :type cdp_dump_path: str
        """
        
        self.web_connection = WebConnection()
        self.web_constants = web_constants
        self.commit_url = web_constants.commit_url_paginated
        self.commit_details_url = web_constants.commit_base_url
        self.commit_details = None
        self.project = project
        self.project_name = {CDPConfigValues.configFetcher.get('name', project)}
        self.cdp_dump_path = f"{CDPConfigValues.cdp_dump_path}/{self.project_name}"
        CDPConfigValues.create_directory(self.cdp_dump_path)

    def get_commit_data_asyncio(self):
        """
        method to find commit details using github APIs
        :returns: commit data
        :rtype: list
        """
        start_time = time.time()
        commit_data = self.web_connection.get_async_data_using_asyncio_paginated(self.commit_url, self.web_constants, 5)
        end_time = time.time()
        print("Parallel time using (asyncio) =", end_time - start_time)
        return commit_data

    def get_commit_details(self):
        """
        method clones the project repository and collects commit data
        """
        start_time = time.time()
        if CDPConfigValues.use_git_command_to_fetch_commit_details:

            git_data = GitData(self.project)
            git_data.clone_project()

            print("Getting Commit ids using git commands...")
            commit_ids = git_data.get_all_commit_ids()
            commit_ids = list(set(commit_ids))
            commit_ids_data_frame = pd.DataFrame(commit_ids, columns=['Commit_Ids'])
            commit_ids_data_frame.to_csv(f"{self.cdp_dump_path}/{CDPConfigValues.commit_ids_file_name}", index=False)

            print("Getting Commit details using git commands...")
            self.commit_details = git_data.get_all_commit_details(commit_ids_data_frame['Commit_Ids'].to_list())

            self.commit_details.to_csv(f"{self.cdp_dump_path}/{CDPConfigValues.commit_details_file_name}",
                                       encoding='utf-8-sig', index=False)
        else:
            commit_data = self.get_commit_data_asyncio()
            commit_parser = CommitsJsonParser()
            commit_ids = commit_parser.parse_id_listing(commit_data)

            commit_ids = list(set(commit_ids))
            commit_ids_data_frame = pd.DataFrame(commit_ids, columns=['Commit_Ids'])
            commit_ids_data_frame.to_csv(f"{self.cdp_dump_path}/{CDPConfigValues.commit_ids_file_name}", index=False)

            print(f"Total Unique Commit IDs to be fetched is {len(commit_ids)}")
            url_list = Utilities.create_url(self.commit_details_url, commit_ids)

            results = self.web_connection.get_async_data_using_asyncio(url_list, self.web_constants,
                                                                       batch_size=CDPConfigValues.git_api_batch_size)
            commit_details = results[0]
            failed_urls = results[1]
            loop_counter = 1

            while len(failed_urls) > 0 and loop_counter < 20:
                time.sleep(60 * pow(2, loop_counter))

                print(f"Total Failed URL's re-trying {len(failed_urls)}")
                results = self.web_connection.get_async_data_using_asyncio(failed_urls, self.web_constants,
                                                                           CDPConfigValues.git_api_batch_size // 2)
                failed_urls = results[1]
                commit_details = commit_details + results[0]
            self.commit_details = commit_parser.parse_json(commit_details, self.cdp_dump_path)
            self.get_missing_files()

        end_time = time.time()
        print(f"Fetched all commit details in {end_time - start_time}")

    def get_missing_files(self):
        """
        method to fetch file details which are missed due to github limitations
        """

        git_data = GitData(self.project)
        git_data_frame = git_data.get_all_commit_details()

        if len(git_data_frame) > 0:
            os.rename(f"{self.cdp_dump_path}/{CDPConfigValues.commit_details_file_name}",
                      f"{self.cdp_dump_path}/{CDPConfigValues.commit_details_before_merging_with_command_data}")

        data_frame_from_git_command = pd.concat([self.commit_details, git_data_frame], ignore_index=True)
        data_frame_from_git_command.to_csv(f"{self.cdp_dump_path}/{CDPConfigValues.commit_details_file_name}",
                                           encoding='utf-8-sig', index=False)
