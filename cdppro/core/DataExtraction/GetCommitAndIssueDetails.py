import glob
import os
import time
from datetime import datetime, timedelta

import pandas as pd

from DataBaseAccess.RawGitDataInDB import RawGitDataInDB
from DataExtraction.BugAndEventDetails import BugAndEventDetails
from Preprocessing.PreProcessing import Preprocessor
from Utility.CDPConfigValues import CDPConfigValues
from Utility.WebConstants import WebConstants
from VersionControl.GitData import GitData


class PrepareCommitsIssuesDataForPrediction:
    """
        1. Get all new commit data from previous preprocessed file commit id till now
        2. Get all new issues closed data from previous closed issue/events data till now
        3. pre-process newly fetched commit data using previous data
        4. save the preprocessed commit data
        5. return only new commit data

    """

    def __init__(self, project):
        """
        Class Constructor
      
        :param project: unique project id of the project for which data is to be collected
        :type project: str
        :param project_name: project name of the project for which data is to be collected
        :type project_name: str
        :param web_constants: object of web_constants class. It contains constant details like different github URLs about any project.
        :type web_constants: Object
        :param previous_preprocessed_df: dataframe containing previously processed data
        :type previous_preprocessed_df: : Pandas Dataframe
        :param previous_bug_list_df: dataframe containing previously processed bugs data
        :type previous_bug_list_df: Pandas Dataframe
        :param previous_events_df: dataframe containing previously processed events data
        :type previous_events_df: Pandas Dataframe
        :param previous_preprocessed_file: file path of previously processed data
        :type previous_preprocessed_file: str
        :param commit_ids: List of commit ids to be processed
        :type commit_ids: list
        :param commit_details: commit details for commit ids to be processed
        :type commit_details: str
        :param closed_events_df: dataframe for bugs events
        :type closed_events_df: Pandas Dataframe
        :param current_date: Today's date for which code is running
        :type current_date: date
        :param current_day_directory: directory path to location where all data for a particular project for current date will be stored
        :type current_day_directory: str
        :param previous_closed_events_df
        :type previous_closed_events_df: Pandas Dataframe
        """
        self.project = project
        self.project_name = CDPConfigValues.configFetcher.get('name', project)
        self.web_constants = WebConstants(project)
        self.previous_preprocessed_df = pd.DataFrame()
        self.previous_bug_list_df = pd.DataFrame()
        self.previous_events_df = pd.DataFrame()
        self.previous_preprocessed_file = ""
        self.commit_ids = ""
        self.commit_details = ""
        self.closed_events_df = ""
        self.current_date = datetime.today().strftime('%Y-%m-%d')
        self.current_day_directory = f"{CDPConfigValues.schedule_file_path}/{self.project_name}/{self.current_date}"
        CDPConfigValues.create_directory(self.current_day_directory)
        self.previous_closed_events_df = ""

    def get_previous_preprocessed_file(self, file_name):
        """
        internal method to return path of previous preprocessed file
        :param file_name: Final Feature File name
        :type file_name: str
        :returns: Path of latest Final Feature File
        :rtype: str
        """
        directory = f"{CDPConfigValues.schedule_file_path}/{self.project_name}/**/{file_name}"

        files = glob.glob(directory, recursive=True)
        if len(files) == 0:
            return None
        files.sort()
        return os.path.realpath(files[-1])

    def get_commit_and_bug_data(self):
        """
        method checks the previous data present in database and accordingly collects new data for commits and bugs for prediction.
        """
        last_imported_predicted_timestamp_db = self.current_date
        last_imported_predicted_timestamp_file = self.current_date
        if not os.path.exists(f"{self.current_day_directory}/{CDPConfigValues.commit_details_file_name}"):
            print("Fetching Latest Commit Details...")
            file_name = CDPConfigValues.final_feature_file
            print(f"Previous File Name : {file_name}")
            self.previous_preprocessed_file = self.get_previous_preprocessed_file(file_name)
            print(f"Previous File Path : {self.previous_preprocessed_file}")

            self.previous_preprocessed_df = pd.read_csv(self.previous_preprocessed_file)
            self.previous_preprocessed_df.to_csv(f"{self.current_day_directory}/previous_preprocessed_df.csv",
                                                 index=False)
            raw_git_data = RawGitDataInDB(self.project)
            raw_git_data.get_project_id()
            query_date = (datetime.today().utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
            imported_predicted_git_data = raw_git_data.fetch_commit_data(query_date)

            if imported_predicted_git_data is not None and len(imported_predicted_git_data) != 0:
                try:
                    imported_predicted_git_data = imported_predicted_git_data.sort_values(by=["TIMESTAMP"],
                                                                                          ascending=[True])

                    last_imported_predicted_timestamp_db = \
                        pd.Timestamp(imported_predicted_git_data["TIMESTAMP"].to_list()[-1])
                    last_imported_predicted_timestamp_db = str(last_imported_predicted_timestamp_db).split(' ')[0]
#                    print("last imported timestamp ", last_imported_predicted_timestamp)

                    last_imported_predicted_timestamp_db = last_imported_predicted_timestamp_db.split(' ')[0]

                except Exception as e:
                    """
                    Part of hack as due to raw data size large, it is throwing error while inserting the data in DB.
                    Once that bug is resolved, entire exception part need to be removed.
                    """
                    print(e)
                    self.previous_preprocessed_df = pd.read_csv(self.previous_preprocessed_file)
                    self.previous_preprocessed_df = self.previous_preprocessed_df.sort_values(
                        by=["COMMITTER_TIMESTAMP"], ascending=[True])
                    last_imported_predicted_timestamp_file = self.previous_preprocessed_df["COMMITTER_TIMESTAMP"].to_list()[-1]

                    self.previous_preprocessed_df.to_csv(f"{self.current_day_directory}/previous_preprocessed_df.csv",
                                                         index=False)
                    last_imported_predicted_timestamp_file = last_imported_predicted_timestamp_file.split(' ')[0]

            
            self.previous_preprocessed_df = pd.read_csv(self.previous_preprocessed_file)
            self.previous_preprocessed_df = self.previous_preprocessed_df.sort_values(by=["COMMITTER_TIMESTAMP"],
                                                                                      ascending=[True])
            last_imported_predicted_timestamp_file = self.previous_preprocessed_df["COMMITTER_TIMESTAMP"].to_list()[-1]

            self.previous_preprocessed_df.to_csv(f"{self.current_day_directory}/previous_preprocessed_df.csv",
                                                     index=False)
            last_imported_predicted_timestamp_file = last_imported_predicted_timestamp_file.split(' ')[0]
            if last_imported_predicted_timestamp_db < last_imported_predicted_timestamp_file:
                last_imported_git_timestamp = last_imported_predicted_timestamp_db
            else:
                last_imported_git_timestamp = last_imported_predicted_timestamp_file

            git_data = GitData(self.project)
            self.commit_ids = git_data.get_all_commit_ids_from_date(last_imported_git_timestamp)
            self.commit_details = git_data.get_all_commit_details(self.commit_ids)

            print(f"Latest commit Details Shape: {self.commit_details.shape} an Length: {len(self.commit_details)}")
            if len(self.commit_details) != 0:
                print(f"Previous Commit File Shape : {self.previous_preprocessed_df.shape}")
                self.commit_details = self.commit_details[
                    ~(self.commit_details.COMMIT_ID.isin(self.previous_preprocessed_df.COMMIT_ID))]

                print(f"Current Commit File Shape after removing previous commits : {self.commit_details.shape}")

            self.commit_details.to_csv(f"{self.current_day_directory}/{CDPConfigValues.commit_details_file_name}",
                                       index=False)
        else:
            print("Latest Commit Details already Present...")
            try:
                self.commit_details = pd.read_csv(
                    f"{self.current_day_directory}/{CDPConfigValues.commit_details_file_name}")
            except pd.errors.EmptyDataError:
                print('Note: filename.csv was empty. Skipping.')
                self.commit_details = pd.DataFrame()
            except pd.io.common.EmptyDataError:
                print('Note: filename.csv was empty. Skipping.')
                self.commit_details = pd.DataFrame()

        if not os.path.exists(f"{self.current_day_directory}/{CDPConfigValues.closed_events_list_file_name}"):
            print("Fetching Latest Issue Details...")
            bug_data_file = CDPConfigValues.project_issue_list_file_name
            print(bug_data_file)
            previous_bug_data_file = self.get_previous_preprocessed_file(bug_data_file)
            self.previous_bug_list_df = pd.read_csv(previous_bug_data_file)

            closed_event_data_file = CDPConfigValues.closed_events_list_file_name
            previous_closed_event_file = self.get_previous_preprocessed_file(closed_event_data_file)
            self.previous_closed_events_df = pd.read_csv(previous_closed_event_file)

            events_data_frame = CDPConfigValues.github_events_cdp_dump
            previous_event_file = self.get_previous_preprocessed_file(events_data_frame)
            if previous_event_file is not None:
                self.previous_events_df = pd.read_csv(previous_event_file)

            if len(self.commit_details) != 0:
                bug_event_details = BugAndEventDetails(self.web_constants, self.project)
                self.closed_events_df = bug_event_details.get_events_data_for_scheduler(self.current_date,
                                                                                        self.previous_bug_list_df,
                                                                                        self.previous_closed_events_df)
                if self.closed_events_df is None:
                    self.closed_events_df = self.previous_closed_events_df
            else:
                self.closed_events_df = self.previous_closed_events_df

            self.closed_events_df.to_csv(f"{self.current_day_directory}/{CDPConfigValues.closed_events_list_file_name}",
                                         index=False)
        else:
            print("Latest Issue Details already Present...")
            self.closed_events_df = pd.read_csv(
                f"{self.current_day_directory}/{CDPConfigValues.closed_events_list_file_name}")

    def filter_data_frame(self, data_frame):
        """
        internal method to filter files in a project based on their extensions.
        :param data_frame: data_frame to be filtered
        :type data_frame: Pandas Dataframe
        :returns: filtered dataframe
        :rtype: Pandas dataframe
        """
        if self.project_name == "spring-boot":
            data_frame = data_frame[data_frame["FILE_NAME"].str.endswith(".java")]
        elif self.project_name == "opencv":
            data_frame = data_frame[
                (data_frame["FILE_NAME"].str.endswith(".hpp") |
                 data_frame["FILE_NAME"].str.endswith(".cpp") |
                 data_frame["FILE_NAME"].str.endswith(".h") |
                 data_frame["FILE_NAME"].str.endswith(".cc") |
                 data_frame["FILE_NAME"].str.endswith(".c") |
                 data_frame["FILE_NAME"].str.endswith(".py") |
                 data_frame["FILE_NAME"].str.endswith(".java") |
                 data_frame["FILE_NAME"].str.endswith(".cl") |
                 data_frame["FILE_NAME"].str.endswith(".cs"))]
        elif self.project_name == "corefx":
            data_frame = data_frame[
                (data_frame["FILE_NAME"].str.endswith(".cs") |
                 data_frame["FILE_NAME"].str.endswith(".h") |
                 data_frame["FILE_NAME"].str.endswith(".c") |
                 data_frame["FILE_NAME"].str.endswith(".vb"))]

        return data_frame

    def pre_process_data(self):
        """
        method reads latest commits data collected by get_commit_and_bug_data and processes it.
        
        :returns: Preprocessed dataframe
        :rtype: Pandas Dataframe
        """
        preprocessor = None
        if os.path.exists(f"{self.current_day_directory}/intermediate_file.csv"):
            print("Reading From intermediate_file.csv")
            self.commit_details = pd.read_csv(f"{self.current_day_directory}/intermediate_file.csv")
            preprocessor = Preprocessor(self.project, self.commit_details, preprocessed=True)
        else:
            print(f"Reading From {self.current_day_directory}/{CDPConfigValues.commit_details_file_name}")
            print(f"Latest commit Details Shape: {self.commit_details.shape} an Length: {len(self.commit_details)}")
            try:
                self.commit_details = pd.read_csv(
                    f"{self.current_day_directory}/{CDPConfigValues.commit_details_file_name}")
                if len(self.commit_details) != 0:
                    preprocessor = Preprocessor(self.project, self.commit_details)
            except pd.errors.EmptyDataError:
                print('Note: filename.csv was empty. Skipping.')
                self.commit_details = pd.DataFrame()
            except pd.io.common.EmptyDataError:
                print('Note: filename.csv was empty. Skipping.')
                self.commit_details = pd.DataFrame()

        if preprocessor is not None:
            self.commit_details = preprocessor.github_data_dump_df
            self.commit_details = self.filter_data_frame(self.commit_details)

        if len(self.commit_details) != 0:

            preprocessor.github_data_dump_df = self.commit_details

            columns = list(self.commit_details.columns)
            if "MONTH" not in columns:
                preprocessor.convert_month_day_date_hour_to_categorical()
            if "IsFix" not in columns:
                preprocessor.file_status_to_categorical()
                preprocessor.determine_commit_is_fix(self.closed_events_df)
                self.commit_details = preprocessor.github_data_dump_df
                self.commit_details.to_csv(f"{CDPConfigValues.schedule_file_path}/{self.project_name}/"
                                           f"{self.current_date}/{CDPConfigValues.intermediate_file}", index=False)
            if "FILE_SIZE" not in columns:
                preprocessor.get_file_size()
                self.commit_details = preprocessor.github_data_dump_df
                self.commit_details.to_csv(
                    f"{self.current_day_directory}/intermediate_file.csv",
                    index=False)

            self.previous_preprocessed_df = pd.read_csv(f"{self.current_day_directory}/previous_preprocessed_df.csv")

            data_frame_for_concatenating = \
                self.previous_preprocessed_df[["COMMIT_ID", "COMMIT_MESSAGE", "AUTHOR_NAME", "AUTHOR_EMAIL",
                                               "AUTHOR_TIMESTAMP", "COMMITTER_NAME", "COMMITTER_EMAIL",
                                               "COMMITTER_TIMESTAMP", "FILE_NAME", "FILE_STATUS", "LINES_ADDED",
                                               "LINES_MODIFIED", "LINES_DELETED", "NF", "ND", "FILES_ENTROPY",
                                               "FILE_URL",
                                               "DAY", "MONTH", "DATE", "HOUR", "SUNDAY", "MONDAY", "TUESDAY",
                                               "WEDNESDAY",
                                               "THURSDAY", "FRIDAY", "SATURDAY", "IsFix", "FILE_SIZE"]]

            self.commit_details = \
                self.commit_details[["COMMIT_ID", "COMMIT_MESSAGE", "AUTHOR_NAME", "AUTHOR_EMAIL",
                                     "AUTHOR_TIMESTAMP", "COMMITTER_NAME", "COMMITTER_EMAIL",
                                     "COMMITTER_TIMESTAMP", "FILE_NAME", "FILE_STATUS", "LINES_ADDED",
                                     "LINES_MODIFIED", "LINES_DELETED", "NF", "ND", "FILES_ENTROPY", "FILE_URL",
                                     "DAY", "MONTH", "DATE", "HOUR", "SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY",
                                     "THURSDAY", "FRIDAY", "SATURDAY", "IsFix", "FILE_SIZE"]]

            data_frame_for_concatenating = pd.DataFrame(data_frame_for_concatenating)

            self.commit_details = \
                pd.concat([self.commit_details, data_frame_for_concatenating], ignore_index=True)

            self.commit_details = self.filter_data_frame(self.commit_details)
            preprocessor.github_data_dump_df = self.commit_details

            self.commit_details.to_csv(f"{CDPConfigValues.schedule_file_path}/{self.project_name}/"
                                       f"{self.current_date}/{CDPConfigValues.intermediate_file}", index=False)

            preprocessor.github_data_dump_df = self.commit_details
            preprocessor.get_sub_module_stats()
            self.commit_details = preprocessor.github_data_dump_df
            self.commit_details.to_csv(f"{CDPConfigValues.schedule_file_path}/{self.project_name}/"
                                       f"{self.current_date}/{CDPConfigValues.intermediate_file}", index=False)

            preprocessor.get_commit_file_age_and_number_of_developer_mp()
            preprocessor.get_developer_experience_using_mp(True)
            preprocessor.get_developer_experience_using_mp(False)
            preprocessor.get_developer_stats()
            preprocessor.get_commit_type()
            preprocessor.calculate_file_changes()
            final_feature_file = preprocessor.github_data_dump_df
            preprocessor.drop_unnecessary_columns()
            preprocessor.rename()
            preprocessor.get_no_of_files_count()
            preprocessor.update_file_name_directory()
            preprocessor.get_no_of_directories_count()
            self.commit_details = preprocessor.github_data_dump_df
            self.commit_details.to_csv(f"{CDPConfigValues.schedule_file_path}/{self.project_name}/"
                                       f"{self.current_date}/{CDPConfigValues.intermediate_file}", index=False)

            final_feature_file.to_csv(f"{CDPConfigValues.schedule_file_path}/{self.project_name}/"
                                      f"{self.current_date}/{CDPConfigValues.final_feature_file}", index=False)

            return self.commit_details

        else:
            self.previous_preprocessed_df = self.filter_data_frame(self.previous_preprocessed_df)
            self.previous_preprocessed_df.to_csv(f"{CDPConfigValues.schedule_file_path}/{self.project_name}"
                                                 f"/{self.current_date}/{CDPConfigValues.final_feature_file}",
                                                 index=False)
            return self.previous_preprocessed_df


if __name__ == "__main__":

    for key in sorted(CDPConfigValues.cdp_projects.keys()):
        if key == "project_1":
            prediction = PrepareCommitsIssuesDataForPrediction(key)
            start_time = time.time()
            prediction.get_commit_and_bug_data()
            prediction.pre_process_data()
            end_time = time.time()
            print(f"Time Taken to complete Pre-processing {end_time - start_time}")
