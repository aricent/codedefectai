# import start
import ast
import asyncio
import calendar
import platform
import subprocess as sp
import time
import traceback
import xml.etree.ElementTree as Et
from collections import defaultdict
from datetime import datetime

import math
import numpy as np
import pandas as pd

from Utility.CDPConfigValues import CDPConfigValues
from Utility.Utilities import Utilities
from Utility.WebConstants import WebConstants
from WebConnection.WebConnection import WebConnection
# import end

## Function to reverse a string
#def reverse(string):
#    string = string[::-1]
#    return string


class Preprocessor:
    """ Preprocessor class is used for preparing the extracted data to be fed to the training algorithm
        for further processing.        
    """
    def __init__(self, project, previous_preprocessed_df=None, preprocessed=None):
        """
        :param timestamp_column: Contains the committer timestamp
        :type timestamp_column: str
        
        :param email_column: Contains the committer timestamp
        :type email_column: str
        
        :param project: project key to be processed
        :type project: str
        
        :param project_name: project name to be processed
        :type project_name: str
        
        :param web_constants: Constants load from file
        :type web_constants: class WebConstants
        
        :param base_timestamp: Instantiating committer timestamp
        :type base_timestamp: str
        
        :param developer_stats_df: creating dataframe variable for developer stats
        :type developer_stats_df: pandas dataframe
        
        :param developer_sub_module_stats_df: creating dataframe variable for developer sub module stats
        :type developer_sub_module_stats_df: pandas dataframe
        
        """
        self.timestamp_column = "COMMITTER_TIMESTAMP"
        self.email_column = "COMMITTER_EMAIL"
        self.project = project
        self.project_name = CDPConfigValues.configFetcher.get('name', project)
        self.web_constants = WebConstants(project)
        self.base_timestamp = ""
        self.developer_stats_df = ""
        self.developer_sub_module_stats_df = ""
        if preprocessed is None:
            if previous_preprocessed_df is None:
                self.file_path = f"{CDPConfigValues.preprocessed_file_path}/{self.project_name}"

                self.github_data_dump_df = pd.read_csv(
                    f"{CDPConfigValues.cdp_dump_path}/{self.project_name}/{CDPConfigValues.commit_details_file_name}")

                self.pre_processed_file_path = f"{CDPConfigValues.preprocessed_file_path}/{self.project_name}"
                CDPConfigValues.create_directory(self.pre_processed_file_path)

                self.stats_dataframe = pd.DataFrame()
                self.sub_module_list = list()

            else:
                self.file_path = f"{CDPConfigValues.schedule_file_path}/{self.project_name}"
                self.github_data_dump_df = pd.DataFrame(previous_preprocessed_df)

            self.github_data_dump_df = self.github_data_dump_df.apply(
                lambda x: x.str.strip() if x.dtype == "object" else x)

            self.github_data_dump_df["COMMITTER_TIMESTAMP"] = self.github_data_dump_df["COMMITTER_TIMESTAMP"].apply(
                lambda x: pd.Timestamp(x, tz="UTC"))
            self.github_data_dump_df["COMMITTER_TIMESTAMP"] = self.github_data_dump_df["COMMITTER_TIMESTAMP"].apply(
                lambda x: pd.Timestamp(x))

            self.github_data_dump_df['COMMITTER_TIMESTAMP'] = self.github_data_dump_df['COMMITTER_TIMESTAMP'].astype(
                str)

            self.github_data_dump_df['COMMITTER_TIMESTAMP'] = self.github_data_dump_df['COMMITTER_TIMESTAMP'].apply(
                lambda x: x[:-6])
            self.filter_data_frame(self.github_data_dump_df)

            if self.github_data_dump_df.shape[0] != 0:
                self.github_data_dump_df["COMMITTER_EMAIL"] = \
                    self.github_data_dump_df[["COMMITTER_EMAIL", "COMMITTER_NAME"]].apply(self.replace_blank_email, axis=1)
        else:
            self.github_data_dump_df = previous_preprocessed_df

    @staticmethod
    def replace_blank_email(row):
        if row["COMMITTER_EMAIL"] is None or row["COMMITTER_EMAIL"] == "":
            return str(row["COMMITTER_NAME"]).replace(" ", "") + "@noemail"
        else:
            return row["COMMITTER_EMAIL"]

    def filter_data_frame(self, data_frame):

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
                 data_frame["FILE_NAME"].str.endswith(".cl")
                 )]
            # data_frame["FILE_NAME"].str.endswith(".cs")
        elif self.project_name == "corefx":
            data_frame = data_frame[
                (data_frame["FILE_NAME"].str.endswith(".cs") |
                 data_frame["FILE_NAME"].str.endswith(".h") |
                 data_frame["FILE_NAME"].str.endswith(".c") |
                 data_frame["FILE_NAME"].str.endswith(".vb"))]
        self.github_data_dump_df = data_frame



    def convert_month_day_date_hour_to_categorical(self, ):
        """
            This method takes the month, day and hour and applies one hot encoding manually
        """
        convert_date_to_categorical_start_time = time.time()
        timestamp_column_in_df = self.github_data_dump_df['COMMITTER_TIMESTAMP']

        dayList = list()
        monthList = list()
        dateList = list()
        hourList = list()
        mondayList = list()
        tuesdayList = list()
        wednesdayList = list()
        thursdayList = list()
        fridayList = list()
        saturdayList = list()
        sundayList = list()

        for timestamp_value in timestamp_column_in_df:
            new_date_format = datetime.strptime(timestamp_value, '%Y-%m-%d %H:%M:%S')
            weekdayStr = calendar.day_name[new_date_format.weekday()]
            dayList.append(weekdayStr)

            if weekdayStr == 'Sunday':
                sundayList.append('1')
                mondayList.append('0')
                tuesdayList.append('0')
                wednesdayList.append('0')
                thursdayList.append('0')
                fridayList.append('0')
                saturdayList.append('0')
            elif weekdayStr == 'Monday':
                sundayList.append('0')
                mondayList.append('1')
                tuesdayList.append('0')
                wednesdayList.append('0')
                thursdayList.append('0')
                fridayList.append('0')
                saturdayList.append('0')
            elif weekdayStr == 'Tuesday':
                sundayList.append('0')
                mondayList.append('0')
                tuesdayList.append('1')
                wednesdayList.append('0')
                thursdayList.append('0')
                fridayList.append('0')
                saturdayList.append('0')
            elif weekdayStr == 'Wednesday':
                sundayList.append('0')
                mondayList.append('0')
                tuesdayList.append('0')
                wednesdayList.append('1')
                thursdayList.append('0')
                fridayList.append('0')
                saturdayList.append('0')
            elif weekdayStr == 'Thursday':
                sundayList.append('0')
                mondayList.append('0')
                tuesdayList.append('0')
                wednesdayList.append('0')
                thursdayList.append('1')
                fridayList.append('0')
                saturdayList.append('0')
            elif weekdayStr == 'Friday':
                sundayList.append('0')
                mondayList.append('0')
                tuesdayList.append('0')
                wednesdayList.append('0')
                thursdayList.append('0')
                fridayList.append('1')
                saturdayList.append('0')
            elif weekdayStr == 'Saturday':
                sundayList.append('0')
                mondayList.append('0')
                tuesdayList.append('0')
                wednesdayList.append('0')
                thursdayList.append('0')
                fridayList.append('0')
                saturdayList.append('1')

            monthList.append(new_date_format.month)
            dateList.append(new_date_format.day)
            hourList.append(new_date_format.hour)

        self.github_data_dump_df['DAY'] = dayList
        self.github_data_dump_df['MONTH'] = monthList
        self.github_data_dump_df['DATE'] = dateList
        self.github_data_dump_df['HOUR'] = hourList
        self.github_data_dump_df['SUNDAY'] = sundayList
        self.github_data_dump_df['MONDAY'] = mondayList
        self.github_data_dump_df['TUESDAY'] = tuesdayList
        self.github_data_dump_df['WEDNESDAY'] = wednesdayList
        self.github_data_dump_df['THURSDAY'] = thursdayList
        self.github_data_dump_df['FRIDAY'] = fridayList
        self.github_data_dump_df['SATURDAY'] = saturdayList

        convert_date_to_categorical_end_time = time.time()
        print(f"Time taken to convert datetime to Categorical is "
              f"{convert_date_to_categorical_end_time - convert_date_to_categorical_start_time}")

    @staticmethod
    def file_status_to_cat(value):
        """
            THelper method for replacing string to single character value
        """
        if value == 'modified':
            return 'M'
        elif value == 'added':
            return 'A'
        elif value == 'renamed':
            return 'R'
        else:
            return 'D'


    def file_status_to_categorical(self, ):
        """
            This method modifies the string value of the file status to categorical (single character)
        """
        file_status_start_time = time.time()
        self.github_data_dump_df['FILE_STATUS'] = self.github_data_dump_df['FILE_STATUS'].apply(self.file_status_to_cat)
        file_status_end_time = time.time()
        print(f"Time Taken to convert file status to categorical {file_status_end_time - file_status_start_time}")

    def determine_commit_is_fix(self, closed_events_df=None):
        """
            This method modifies the dataframe to label commits as isFix corresponding to commmits
            
            :param closed_events_df: dataframe containing the closed events list
            :type closed_events_df: pandas dataframe
            
        """

        commit_isFix_start_time = time.time()
        if closed_events_df is None:
            closed_issue_df = pd.read_csv(
                f"{CDPConfigValues.cdp_dump_path}/{self.project_name}/{CDPConfigValues.closed_events_list_file_name}")
        else:
            closed_issue_df = closed_events_df

        commits_closed_df = pd.DataFrame(
            closed_issue_df.loc[closed_issue_df["commitid"] != ""]["commitid"].drop_duplicates())
        commits_closed_df = commits_closed_df.dropna()
        commits_closed_df.columns = ["COMMIT_ID"]

        search_pattern = "|".join(commits_closed_df["COMMIT_ID"].to_list())
        isFix = self.github_data_dump_df["COMMIT_ID"].str.contains(search_pattern)
        self.github_data_dump_df["IsFix"] = isFix.replace((True, False), (1, 0))

        commit_isFix_end_time = time.time()
        print(f"Time Taken for determining for Commit is for Fix {commit_isFix_end_time - commit_isFix_start_time}")

    def get_commit_type(self):
        """
            This method based on the commit message containing merge text labels each record as a merge or non-merge
            commit.
        """
        commit_type_start_time = time.time()
        search_pattern = "|".join(["Merge pull request"])
        isFix = self.github_data_dump_df["COMMIT_MESSAGE"].str.contains(search_pattern)
        self.github_data_dump_df["COMMIT_TYPE"] = isFix.replace((True, False), (1, 0))
        commit_type_end_time = time.time()
        print(f"Time Taken for getting commit type is {commit_type_end_time - commit_type_start_time}")

    def get_file_size(self, ):
        """
            The method extracts the file size using the github rest URL service for each commit and corresponding 
            files.
        """

        file_age_start_time = time.time()

        self.github_data_dump_df = self.github_data_dump_df.sort_values(by=["COMMITTER_TIMESTAMP"],
                                                                        ascending=[True])
        commit_id_list = self.github_data_dump_df["COMMIT_ID"].drop_duplicates().to_list()

        print(f"Total Content Urls to be requested {len(commit_id_list)}")

        file_size_url_list = Utilities.format_url(self.web_constants.file_size_url, commit_id_list)
        batch_size = int(CDPConfigValues.git_api_batch_size)
        web_connection = WebConnection()
        results = web_connection.get_async_file_size(file_size_url_list, self.github_data_dump_df, self.web_constants,
                                                     batch_size)
        file_size = results[0]
        failed_urls = results[1]
        loop_counter = 1

        while len(failed_urls) > 0 and loop_counter < 200:
            loop_counter = loop_counter + 1
            print(f"Sleeping for {60 * loop_counter} Seconds in get_file_size ...")
            time.sleep(60 * loop_counter)
            print(f"Total Failed URL's re-trying {len(failed_urls)}")
            results = web_connection.get_async_file_size(failed_urls, self.github_data_dump_df, self.web_constants,
                                                         batch_size=batch_size)
            failed_urls = results[1]
            file_size = file_size + results[0]

        file_size_df = pd.DataFrame(file_size, columns=["COMMIT_ID", "FILE_NAME", "FILE_SIZE"])
        file_size_df = file_size_df.drop_duplicates()
        file_size_df = file_size_df.sort_values(by=["COMMIT_ID"])

        self.github_data_dump_df = self.github_data_dump_df.sort_values(by=["COMMIT_ID"])

        self.github_data_dump_df = pd.merge(self.github_data_dump_df, file_size_df, how="left",
                                            left_on=["COMMIT_ID", "FILE_NAME"], right_on=["COMMIT_ID", "FILE_NAME"])
        file_age_end_time = time.time()
        print(f"Fetched all file sizes in {file_age_end_time - file_age_start_time}")

    @staticmethod
    async def calculate_commit_file_age_and_number_of_developer_mp(file_df, file_name):
        """
            The method is a helper method which calculates the file age and number of developers for a single file
            
            :param file_df: dataframe containing the file details
            :type file_df: pandas dataframe
            
            :param file_name: Name of the file
            :type file_name: str
        """

        number_of_developers, file_age = list(), list()
        counter = 0
        df_len = len(file_df)
        result = defaultdict()
        # file_age_normal = list()

        while counter < df_len:
            # Changed as part of review comment
            # if counter == 0 or file_df["FILE_STATUS"].iloc[counter] == "A":
            if counter == 0:
                file_age.append(0)
                # file_age_normal.append(0)
            elif counter > 0:

                # file_age_normal.append(
                #     (file_df["COMMITTER_TIMESTAMP"].iloc[counter] - file_df["COMMITTER_TIMESTAMP"].iloc[
                #         counter - 1]))
                age = (file_df["COMMITTER_TIMESTAMP"].iloc[counter] - file_df["COMMITTER_TIMESTAMP"].iloc[
                    counter - 1]).days * 24 * 3600 + \
                      (file_df["COMMITTER_TIMESTAMP"].iloc[counter] - file_df["COMMITTER_TIMESTAMP"].iloc[
                          counter - 1]).seconds
                file_age.append(age)

            current_timestamp = file_df["COMMITTER_TIMESTAMP"].iloc[counter]

            # if file_df["FILE_STATUS"].iloc[counter] == "A":
            # Changed as part of review comment
            if counter == 0:
                number_of_developers.append(1)
            else:
                number_of_developers.append(
                    len(set(file_df.loc[file_df["COMMITTER_TIMESTAMP"] <= current_timestamp]["COMMITTER_NAME"])))

            counter = counter + 1
        await asyncio.sleep(0)
        result[file_name] = (file_age, number_of_developers)

        return result

    async def execute_calculate_commit_file_age_and_number_of_developer_mp(self, batch):
        result = await asyncio.gather(
            *[self.calculate_commit_file_age_and_number_of_developer_mp(
                self.github_data_dump_df.loc[self.github_data_dump_df["FILE_NAME"] == file][
                    ["COMMIT_ID", "COMMITTER_NAME", "FILE_STATUS", "COMMITTER_TIMESTAMP"]], file) for file in batch]
        )
        return result

    def get_commit_file_age_and_number_of_developer_mp(self, ):
        """
            The method calculates the file age which is difference of current change and the last change 
            for that file. The other output is the number of developers who have worked on that file.
        """
        commit_age_no_of_dev_start_time = time.time()

        self.github_data_dump_df["COMMITTER_TIMESTAMP"] = pd.to_datetime(
            self.github_data_dump_df["COMMITTER_TIMESTAMP"])

        self.github_data_dump_df = self.github_data_dump_df.sort_values(by=["FILE_NAME", "COMMITTER_TIMESTAMP"],
                                                                        ascending=[True, True])
        file_names = self.github_data_dump_df["FILE_NAME"]
        file_names = file_names.drop_duplicates().to_list()

        commit_file_age, number_of_developers, failed_batches = list(), list(), list()

        results = defaultdict()
        batch_size = 100
        file_batches = list(Utilities.create_batches(file_names, batch_size=batch_size))
        print(f"For Getting Commit File Age and Numbre of Developers,  Batch size {batch_size}")
        total_batches = len(file_batches)
        batch_counter, percent = 0, 0
        print(f"Total Batches to be executed for getting commit file age and number of developer is {total_batches}")
        for batch in file_batches:
            try:
                loop = asyncio.get_event_loop()
                asyncio.set_event_loop(asyncio.new_event_loop())

                if (total_batches * percent) // 100 == batch_counter:
                    print(
                        f"Total Batches completed is {batch_counter} and Failed batches Count is {len(failed_batches)}")
                    percent = percent + 10

                results_list = loop.run_until_complete(
                    self.execute_calculate_commit_file_age_and_number_of_developer_mp(batch))
                for result in results_list:
                    for result_key in result.keys():
                        results[result_key] = result[result_key]
            except Exception as e:
                print(f"Exception Occurred!!!\n{traceback.print_tb(e.__traceback__)}")
                for file_name in batch:
                    failed_batches.append(file_name)
            batch_counter = batch_counter + 1

        """Retrieving the result of the dictionary on sorted order of the keys (author is the result_key)"""

        for result_key in sorted(results.keys()):
            commit_file_age = commit_file_age + results[result_key][0]
            number_of_developers = number_of_developers + results[result_key][1]

        self.github_data_dump_df["FILE_AGE"] = commit_file_age
        self.github_data_dump_df["NO_OF_DEV"] = number_of_developers

        commit_age_no_of_dev_end_time = time.time()
        print(f"Time Taken FILE_AGE and NO_OF_DEV {commit_age_no_of_dev_end_time - commit_age_no_of_dev_start_time}")

    async def calculate_developer_experience(self, file_df, author_name):
        """
            Helper method for developer experience 
        """

        file_df["Year"] = (pd.to_datetime(self.base_timestamp) - pd.to_datetime(file_df["COMMITTER_TIMESTAMP"])) / (
                np.timedelta64(1, 'D') * 365)
        file_df["Year"] = file_df["Year"].apply(lambda x: math.ceil(x) + 1)

        unique_file_df = file_df
        unique_file_df = unique_file_df.drop_duplicates()

        exp = list()
        dev_exp = defaultdict()
        counter = 0
        while counter < (len(unique_file_df)):
            current_timestamp = unique_file_df["COMMITTER_TIMESTAMP"].iloc[counter]
            commit_id = unique_file_df["COMMIT_ID"].iloc[counter]
            # if counter == 0:
            #     exp.append((commit_id, current_timestamp, 0))
            # else:
            #     year_count = unique_file_df.loc[unique_file_df["COMMITTER_TIMESTAMP"] < current_timestamp][
            #         "Year"].value_counts().rename_axis('Year').reset_index(name='Counts')
            #     year_count["Exp"] = year_count["Counts"] / (year_count["Year"])
            #
            #     exp.append((commit_id, current_timestamp, year_count["Exp"].sum()))
            # year_count = unique_file_df.iloc[counter]

            # Changed as part of review comment
            year_count = unique_file_df.iloc[0:counter + 1][
                "Year"].value_counts().rename_axis('Year').reset_index(name='Counts')

            # year_count = unique_file_df.loc[unique_file_df["COMMITTER_TIMESTAMP"] <= current_timestamp][
            #     "Year"].value_counts().rename_axis('Year').reset_index(name='Counts')
            year_count["Exp"] = year_count["Counts"] / (year_count["Year"])

            exp.append((commit_id, current_timestamp, year_count["Exp"].sum()))

            counter = counter + 1

        exp_df = pd.DataFrame(exp, columns=["COMMIT_ID", "COMMITTER_TIMESTAMP", "EXP"])

        file_df = pd.merge(file_df, exp_df, how="left", left_on=["COMMIT_ID", "COMMITTER_TIMESTAMP"],
                           right_on=["COMMIT_ID", "COMMITTER_TIMESTAMP"])

        await asyncio.sleep(0)
        dev_exp[author_name] = file_df["EXP"].to_list()

        return dev_exp

    async def execute_calculate_developer_experience(self, batch):
        """
            Helper method for developer experience 
        """
        result = await asyncio.gather(
            *[self.calculate_developer_experience(
                self.github_data_dump_df.loc[self.github_data_dump_df["COMMITTER_NAME"] == author_name][
                    ["COMMIT_ID", "COMMITTER_TIMESTAMP"]], author_name) for author_name in batch]
        )

        return result

    @staticmethod
    async def calculate_developer_experience_from_calender_year(file_df, author_name):
        """
            Helper method for developer experience 
        """

        file_df["Year"] = pd.DatetimeIndex(file_df['COMMITTER_TIMESTAMP']).year
        unique_file_df = file_df
        unique_file_df = unique_file_df.drop_duplicates()

        exp = list()
        dev_exp = defaultdict()
        counter = 0
        while counter < (len(unique_file_df)):
            current_timestamp = unique_file_df["COMMITTER_TIMESTAMP"].iloc[counter]
            commit_id = unique_file_df["COMMIT_ID"].iloc[counter]
            if counter == 0:
                exp.append((commit_id, current_timestamp, 0))
            else:
                year_count = unique_file_df.loc[unique_file_df["COMMITTER_TIMESTAMP"] < current_timestamp][
                    "Year"].value_counts().rename_axis('Year').reset_index(name='Counts')
                year_count["Exp"] = year_count["Counts"] / ((datetime.today().year - year_count["Year"]) + 1)
                exp.append((commit_id, current_timestamp, year_count["Exp"].sum()))

            counter = counter + 1

        exp_df = pd.DataFrame(exp, columns=["COMMIT_ID", "COMMITTER_TIMESTAMP", "EXP"])

        file_df = pd.merge(file_df, exp_df, how="left", left_on=["COMMIT_ID", "COMMITTER_TIMESTAMP"],
                           right_on=["COMMIT_ID", "COMMITTER_TIMESTAMP"])

        await asyncio.sleep(0)
        dev_exp[author_name] = file_df["EXP"].to_list()

        return dev_exp

    async def execute_calculate_developer_experience_from_calender_year(self, batch):
        """
            Helper method for developer experience 
        """
        result = await asyncio.gather(
            *[self.calculate_developer_experience_from_calender_year(
                self.github_data_dump_df.loc[self.github_data_dump_df["COMMITTER_NAME"] == author_name][
                    ["COMMIT_ID", "COMMITTER_TIMESTAMP"]], author_name) for author_name in batch]
        )

        return result

    def get_developer_experience_using_mp(self, execution_flag):
        """
            The method calculates developer recent experience based on either 365 days or calendar based calculation.
            It gives higher weight to the experience for first 365 days and so on. Previous years have lower weightage
            
            :param execution_flag: flag to check calculation for 365 or calendar based
            :type execution_flag: bool
        """

        dev_exp_start_time = time.time()

        self.github_data_dump_df = self.github_data_dump_df.sort_values(by=["COMMITTER_TIMESTAMP"],
                                                                        ascending=[True])

        self.base_timestamp = self.github_data_dump_df["COMMITTER_TIMESTAMP"].drop_duplicates().to_list()[-1]

        self.github_data_dump_df = self.github_data_dump_df.sort_values(by=["COMMITTER_NAME", "COMMITTER_TIMESTAMP"],
                                                                        ascending=[True, True])

        failed_batches, developer_exp = list(), list()
        author_exp = defaultdict()
        author_names = self.github_data_dump_df["COMMITTER_NAME"]
        author_names = author_names.drop_duplicates().to_list()
        batch_size = int(CDPConfigValues.configFetcher.get('author_stat_batch_size', self.project))
        author_batches = list(Utilities.create_batches(author_names, batch_size=batch_size))

        print(f"Developer Experience Batch size {batch_size}")
        total_batches = len(author_batches)
        batch_counter, percent = 0, 0
        print(f"Total Batches to be executed for getting Developer Experience is {total_batches}")
        for batch in author_batches:
            try:
                loop = asyncio.get_event_loop()
                asyncio.set_event_loop(asyncio.new_event_loop())

                if (total_batches * percent) // 100 == batch_counter:
                    print(
                        f"Total Batches completed is {batch_counter} and Failed batches Count is {len(failed_batches)}")
                    percent = percent + 10

                if execution_flag:
                    results_list = loop.run_until_complete(
                        self.execute_calculate_developer_experience_from_calender_year(batch))
                else:
                    results_list = loop.run_until_complete(self.execute_calculate_developer_experience(batch))

                for result in results_list:
                    for author_key in result.keys():
                        author_exp[author_key] = result[author_key]

            except Exception as e:
                print(f"Exception Occurred!!!\n{traceback.print_tb(e.__traceback__)}")
                for file_name in batch:
                    failed_batches.append(file_name)
            batch_counter = batch_counter + 1

        """Retrieving the result of the dictionary on sorted order of the keys (author is the author_key)"""
        for author_key in sorted(author_exp.keys()):
            developer_exp = developer_exp + author_exp[author_key]

        if execution_flag:
            self.github_data_dump_df["DEV_REXP_CALENDER_YEAR_WISE"] = developer_exp
        else:
            self.github_data_dump_df["DEV_REXP_365_DAYS_WISE"] = developer_exp

        dev_exp_end_time = time.time()
        print(f"Time Taken For Dev RExperience {dev_exp_end_time - dev_exp_start_time}")

    def parse_xml(self, commit_id, file):
        """
            The method parses the output of the git show command 
            
            :param commit_id: 
            :type commit_id: str
            
            :param file: file 
            :type file: str
        """
        command = f"git show {commit_id}:{file}"

        query = sp.Popen(command, cwd=f"{CDPConfigValues.local_git_repo}/{self.project_name}", stdout=sp.PIPE,
                         stderr=sp.PIPE, shell=True)
        (stdout, sdterr) = query.communicate()
        xml_string = stdout.decode("utf-8", errors='replace')
        tree = Et.fromstring(xml_string)
        submodule = []
        for module in tree.iter():
            if str(module.tag).__contains__("module") and not str(module.tag).__contains__("modules"):
                if module.text != "":
                    if str(module.text).__contains__("/"):
                        submodule.append(str(module.text).split("/")[1])
                    else:
                        submodule.append(module.text)

        # await asyncio.sleep(1)
        return submodule

    def get_submodule_list(self, commit_id):
        """
            THe method based on the commitid retrieves the sub modules impacted for each of the commit 
            
            :param commit_id: 
            :type commit_id: str
        """    

        if platform.system().capitalize() == "Linux":
            command = f"git ls-tree --full-tree -r {commit_id} | grep pom.xml"
        else:
            command = f"git ls-tree --full-tree -r {commit_id} | findstr pom.xml"

        query = sp.Popen(command, cwd=f"{CDPConfigValues.local_git_repo}/{self.project_name}", stdout=sp.PIPE,
                         stderr=sp.PIPE, shell=True)
        (stdout, sdterr) = query.communicate()

        file_list = stdout.decode("utf-8", errors='replace').split("\n")
        sub_module_list = []
        for file in file_list:
            if file != "":
                file_name = file.split('\t')[1]
                if file_name != "":
                    module_list = self.parse_xml(commit_id, file_name)
                    if len(module_list) > 0:
                        sub_module_list = sub_module_list + module_list
        sub_module_list = set(sub_module_list)

        return sub_module_list

    async def execute_submodule_list(self, batch):
        """
            Hepler method
            
            :param batch: commit id batch
            :type batch: list
        """   
        result = await asyncio.gather(
            *[self.get_submodule_list(commit_id) for commit_id in batch]
        )
        return result

    async def get_modules(self, commit_id, file):
        """
            Hepler method
            
            :param commit_id: commit id 
            :type commit_id: str
            
            :param file: file complete name
            :type file: str
        """ 
        sub_modules = file.split("/")
        sub_modules = sub_modules[:-1]
        sub_modules = sub_modules[::-1]
        for sub_module in sub_modules:
            if sub_module in self.sub_module_list:
                result = (commit_id, file, sub_module)
                return result

        if str(file).__contains__('src'):
            if str(file).startswith('/src'):
                if str(file.split('/src')[1]).__contains__('src'):
                    sub_module = file.split('/src')[1].split('/src')[0].split("/")[-1]
                    result = (commit_id, file, sub_module)
                    return result
            else:
                sub_module = file.split('/src')[0].split("/")[-1]
                result = (commit_id, file, sub_module)
                return result

        result = (commit_id, file, "")
        return result

    async def get_sub_modules_and_stats(self, commit_id, file_list):
        """
            Hepler method
            
            :param commit_id: commit id 
            :type commit_id: str
            
            :param file_list: list of file impacted
            :type file_list: list
        """ 
        module_list = []
        result_list = []
        for file in file_list:
            result = await self.get_modules(commit_id, file)
            result_list.append(result)
            if result[2] != "":
                module_list.append(result)

        # module_list = set(module_list)
        result_data_frame = pd.DataFrame(result_list, columns=["COMMIT_ID", "FILE_NAME", "SUB_MODULE"])

        # Changed as part of review comment
        # result_data_frame["NS"] = len(set(module_list))
        result_data_frame["NS"] = len(set(result_data_frame["SUB_MODULE"].to_list()))

        return result_data_frame

    async def execute_sub_module_stat(self, batch):
        result = await asyncio.gather(
            *[self.get_sub_modules_and_stats(commit_id,
                                             self.github_data_dump_df.loc[
                                                 self.github_data_dump_df["COMMIT_ID"] == commit_id][
                                                 "FILE_NAME"].drop_duplicates().to_list()) for commit_id in batch]
        )
        return result

    def get_sub_module_stats(self, ):
        """
            The method complies the sub module statistics for each of the commit. For each of the commit, how many
            sub modules are impacted and is appended as a new column 
            
        """ 

        sub_module_stat_start_time = time.time()
        commit_id_list = self.github_data_dump_df["COMMIT_ID"].drop_duplicates().to_list()
        commit_id_batches = list(Utilities.create_batches(commit_id_list, batch_size=20))
        total_batches = len(commit_id_batches)

        batch_counter, percent = 0, 0
        sub_module_list, failed_batches = list(), list()
        sub_module_stats_df = pd.DataFrame()
        if ast.literal_eval(CDPConfigValues.configFetcher.get('isPOMXmlExists', self.project)):
            self.sub_module_list = list(self.get_submodule_list(commit_id_list[-1]))
        else:
            self.sub_module_list = []

        print(f"Total Batches to be executed for getting sub module count commit wise is {total_batches}")
        for batch in commit_id_batches:
            try:
                loop = asyncio.get_event_loop()
                asyncio.set_event_loop(asyncio.new_event_loop())

                if (total_batches * percent) // 100 == batch_counter:
                    print(
                        f"Total Batches completed is {batch_counter} and Failed batches Count is {len(failed_batches)}")
                    percent = percent + 10

                results_list = loop.run_until_complete(self.execute_sub_module_stat(batch))
                for result in results_list:
                    sub_module_stats_df = pd.concat([sub_module_stats_df, result], ignore_index=True)

            except Exception as e:
                print(f"Exception Occurred!!!\n{traceback.print_tb(e.__traceback__)}")
                for commit_id in batch:
                    failed_batches.append(commit_id)
            batch_counter = batch_counter + 1

        # sub_module_stats_df.to_csv(f"{CDPConfigValues.preprocessed_file_path}/{self.project_name}/SUB_MODULE_FILE.csv",
        #                           index=False)

        self.github_data_dump_df = self.github_data_dump_df.sort_values(by=["COMMIT_ID", "FILE_NAME"],
                                                                        ascending=[True, True])
        sub_module_stats_df = sub_module_stats_df.sort_values(by=["COMMIT_ID", "FILE_NAME"], ascending=[True, True])

        self.github_data_dump_df = pd.merge(self.github_data_dump_df, sub_module_stats_df, how="left",
                                            left_on=["COMMIT_ID", "FILE_NAME"],
                                            right_on=["COMMIT_ID", "FILE_NAME"])
        # self.github_data_dump_df["NS"] = self.github_data_dump_df["NS"].apply(lambda x: 0 if x is None else x)

        sub_module_stat_end_time = time.time()
        print(f"Time Taken For Sub Module Stats Calculation {sub_module_stat_end_time - sub_module_stat_start_time}")

    @staticmethod
    async def developer_stats(data_frame, email, timestamp_column, email_column):
        """
            Helper method            
        """ 
        result_list = []
        data_frame = data_frame.drop_duplicates()
        data_frame = data_frame.sort_values(by=[timestamp_column], ascending=[True])

        dev_data_frame = data_frame[["COMMIT_ID", timestamp_column]].drop_duplicates()

        if len(data_frame) == 0:
            print("Empty Data Frame")
        count = 1

        for index, row in dev_data_frame.iterrows():
            result = (row["COMMIT_ID"], email, row[timestamp_column], count)
            result_list.append(result)
            count = count + 1
        dev_stats_df = pd.DataFrame(result_list, columns=["COMMIT_ID", email_column, timestamp_column, "DEV_STATS"])

        sub_module_list = data_frame["SUB_MODULE"].drop_duplicates().to_list()
        result_list = []

        for sub_module in sub_module_list:
            if sub_module != "":
                count = 0
                sub_module_df = data_frame.loc[data_frame["SUB_MODULE"] == sub_module][["COMMIT_ID", timestamp_column]]
                sub_module_df = sub_module_df.sort_values(by=[timestamp_column], ascending=[True])

                for index, row in sub_module_df.iterrows():
                    result = (row["COMMIT_ID"], email, row[timestamp_column], sub_module, count)
                    result_list.append(result)
                    count = count + 1

        sub_module_stats_df = pd.DataFrame(result_list,
                                           columns=["COMMIT_ID", email_column, timestamp_column, "SUB_MODULE",
                                                    "SUB_MODULE_STATS"])

        result = (dev_stats_df, sub_module_stats_df)
        return result

    async def get_developer_stats_async(self, batch, timestamp_column, email_column):
        """
            Helper method            
        """ 
        result = await asyncio.gather(
            *[self.developer_stats(self.github_data_dump_df.loc[self.github_data_dump_df[email_column] == email]
                                   [["COMMIT_ID", timestamp_column, "SUB_MODULE"]], email, timestamp_column,
                                   email_column)
              for email in batch]
        )

        return result

    def get_developer_stats(self, file_name=None):
        """
            The method complies the developer experience since inception of the projects commit 
            history.
            
            :param file_name: name of the file
            :type file_name: str
            
        """ 

        if file_name is not None:
            self.github_data_dump_df = pd.read_csv(
                f"{CDPConfigValues.preprocessed_file_path}/{self.project_name}/{file_name}")

        self.github_data_dump_df["COMMITTER_EMAIL"] = \
            self.github_data_dump_df[["COMMITTER_EMAIL", "COMMITTER_NAME"]].apply(self.replace_blank_email, axis=1)

        developer_stat_start_time = time.time()

        failed_batches = list()

        email_list = self.github_data_dump_df[self.email_column].drop_duplicates().to_list()
        batch_size= 10
        batches = list(Utilities.create_batches(email_list, batch_size=batch_size))

        print(f"Developer Stats calculation  Batch size {batch_size}")
        total_batches = len(batches)
        batch_counter, percent = 0, 0
        print(f"Total Batches to be executed for getting developer stats is {total_batches}")

        self.developer_stats_df = pd.DataFrame()
        self.developer_sub_module_stats_df = pd.DataFrame()

        for batch in batches:
            try:
                loop = asyncio.get_event_loop()
                asyncio.set_event_loop(asyncio.new_event_loop())

                if (total_batches * percent) // 100 == batch_counter:
                    print(
                        f"Total Batches completed is {batch_counter} and Failed batches Count is {len(failed_batches)}")
                    percent = percent + 10

                results_list = loop.run_until_complete(
                    self.get_developer_stats_async(batch, self.timestamp_column, self.email_column))
                for result in results_list:
                    self.developer_stats_df = pd.concat([self.developer_stats_df, result[0]], ignore_index=True)
                    self.developer_sub_module_stats_df = pd.concat([self.developer_sub_module_stats_df, result[1]],
                                                                   ignore_index=True)

            except Exception as e:
                print(f"Exception Occurred!!!\n{traceback.print_tb(e.__traceback__)}")
                for file_name in batch:
                    failed_batches.append(file_name)

            batch_counter = batch_counter + 1

        # self.developer_stats_df.to_csv(
        #    f"{CDPConfigValues.preprocessed_file_path}/{self.project_name}/{stats_column_name}.csv", index=False)

        self.developer_stats_df = self.developer_stats_df.sort_values(by=[self.email_column, self.timestamp_column],
                                                                      ascending=[True, True])
        self.developer_stats_df = self.developer_stats_df.rename_axis(None)

        self.github_data_dump_df = self.github_data_dump_df.sort_values(by=[self.email_column, self.timestamp_column],
                                                                        ascending=[True, True])

        self.github_data_dump_df = pd.merge(self.github_data_dump_df, self.developer_stats_df, how="left",
                                            left_on=["COMMIT_ID", self.email_column, self.timestamp_column],
                                            right_on=["COMMIT_ID", self.email_column, self.timestamp_column])

        self.developer_sub_module_stats_df = self.developer_sub_module_stats_df.sort_values(
            by=[self.email_column, self.timestamp_column],
            ascending=[True, True])

        self.developer_sub_module_stats_df = self.developer_sub_module_stats_df.rename_axis(None)

        self.github_data_dump_df = pd.merge(self.github_data_dump_df, self.developer_sub_module_stats_df, how="left",
                                            left_on=["COMMIT_ID", self.email_column, self.timestamp_column,
                                                     "SUB_MODULE"],
                                            right_on=["COMMIT_ID", self.email_column, self.timestamp_column,
                                                      "SUB_MODULE"])

        self.github_data_dump_df["SUB_MODULE_STATS"] = self.github_data_dump_df["SUB_MODULE_STATS"].apply(
            lambda x: 0 if x is None else x)
        self.github_data_dump_df["SUB_MODULE_STATS"] = self.github_data_dump_df["SUB_MODULE_STATS"].apply(
            lambda x: 0 if x == "" else x)

        self.github_data_dump_df["SUB_MODULE_STATS"] = self.github_data_dump_df["SUB_MODULE_STATS"].fillna(0)

        developer_stat_end_time = time.time()
        print(f"Time Taken For Author Stat Calculation {developer_stat_end_time - developer_stat_start_time}")

    def get_no_of_files_count(self):
        """
            The method complies the total number of files changed/added for each of the commit
            
        """ 
        # self.github_data_dump_df = pd.read_csv(f"{self.file_path}/old_features_preprocessed_step9.csv")
        self.drop_data_frame_column("NF")
        commit_list = self.github_data_dump_df["COMMIT_ID"].drop_duplicates().to_list()
        result = []
        for commit_id in commit_list:
            result.append((commit_id, len(set(
                self.github_data_dump_df[self.github_data_dump_df["COMMIT_ID"] == commit_id]["FILE_NAME"].to_list()))))

        result_df = pd.DataFrame(result, columns=["COMMIT_ID", "NF"])

        compare_df = pd.DataFrame(self.github_data_dump_df[["COMMIT_ID", "FILE_NAME"]])
        compare_df = compare_df["COMMIT_ID"].value_counts().reset_index()
        # compare_df.columns = ["COMMIT_ID", "FILE_NAME", "NF"]
        #
        # if result_df.equals(compare_df):
        #     print("Two Data Frame are same!!!")

        self.github_data_dump_df = pd.merge(self.github_data_dump_df, result_df, how="left", left_on=["COMMIT_ID"],
                                            right_on=["COMMIT_ID"])

    def get_no_of_directories_count(self):
        """
            The method compiles the total number of unique directories changed/added for each of the commit.
            
        """ 
        self.drop_data_frame_column("ND")

        commit_list = self.github_data_dump_df["COMMIT_ID"].drop_duplicates().to_list()
        result = []
        for commit_id in commit_list:
            result.append((commit_id, len(set(
                self.github_data_dump_df[self.github_data_dump_df["COMMIT_ID"] == commit_id][
                    "FILE_PARENT"].to_list()))))

        result_df = pd.DataFrame(result, columns=["COMMIT_ID", "ND"])

        self.github_data_dump_df = pd.merge(self.github_data_dump_df, result_df, how="left", left_on=["COMMIT_ID"],
                                            right_on=["COMMIT_ID"])

    def update_file_name_directory(self):
        """
            Helper method
            
        """
        fileNameList = list()
        parentFileList = list()
        timeFileModifiedList = list()

        update_file_start_time = time.time()
        filename_directory_column = self.github_data_dump_df['FILE_NAME']

        fileModifiedCountSeries = filename_directory_column.value_counts()
        fileModifiedCountDict = fileModifiedCountSeries.to_dict()

        for value in filename_directory_column:
            noTimesFileModified = fileModifiedCountDict[value]
            timeFileModifiedList.append(noTimesFileModified)
            fileName = value.split('/')[-1]
            parentName = value.split(fileName)[0]
            if parentName is None or parentName == "":
                parentName = "/"
            fileNameList.append(fileName)
            parentFileList.append(parentName)

        self.github_data_dump_df['FILE_PARENT'] = parentFileList
        self.github_data_dump_df['FILE_NAME'] = fileNameList
        self.github_data_dump_df['TIMES_FILE_MODIFIED'] = timeFileModifiedList

        update_file_end_time = time.time()
        print(f"Time Taken to execute update_file_name_directory {update_file_end_time - update_file_start_time}")

    def calculate_file_changes(self):
        """
            The method adds a new feature that calculates the file changes based on number of lines of code added,
            modified or deleted over the number of changes spread across the file (entropy)
            
        """
        
        calculate_file_changes_start_time = time.time()
        self.github_data_dump_df["FileChanges"] = (self.github_data_dump_df["LINES_ADDED"] + self.github_data_dump_df["LINES_MODIFIED"] + self.github_data_dump_df["LINES_DELETED"])/(1 + self.github_data_dump_df["FILES_ENTROPY"])
        calculate_file_changes_end_time = time.time()
        print(f"Time Taken for calculate file changes is {calculate_file_changes_end_time - calculate_file_changes_start_time}")
        # self.github_data_dump_df = self.github_data_dump_df.drop(columns=['LINES_ADDED', 'LINES_MODIFIED', 'FILES_ENTROPY'])

    def drop_data_frame_column(self, column_name):
        """
            The method  drops unused colums from the dataframes
            
            :param column_name: name of the column to be dropped
            :type column_name: str            
        """
        try:
            self.github_data_dump_df = self.github_data_dump_df.drop(column_name, axis=1)
        except Exception as e:
            pass
            print(e)

    def drop_unnecessary_columns(self):
        """
            The method  drops unused colums from the dataframes
                       
        """

        self.drop_data_frame_column('COMMIT_MESSAGE')
        self.drop_data_frame_column('AUTHOR_EMAIL')
        self.drop_data_frame_column('COMMITTER_EMAIL')
        self.drop_data_frame_column('AUTHOR_NAME')
        self.drop_data_frame_column('AUTHOR_TIMESTAMP')
        self.drop_data_frame_column('SUB_MODULE')
        self.drop_data_frame_column('DAY')
        self.drop_data_frame_column('LINES_ADDED')
        self.drop_data_frame_column('LINES_MODIFIED')
        self.drop_data_frame_column('FILES_ENTROPY')
        self.drop_data_frame_column('LINES_DELETED')


    def rename_columns(self, old_name, new_name):
        """
            The method  renames columns to new newname
            
            :param old_name: old column name
            :type old_name: str   
            
            :param new_name: new column name
            :type new_name: str 
        """
        self.github_data_dump_df.columns = [new_name if x == old_name else x for x in self.github_data_dump_df.columns]

    def rename(self):
        """
            The method  renames columns to new newname

        """
        # self.github_data_dump_df = pd.read_csv(f"{self.file_path}/old_features_preprocessed_step12.csv")
        self.rename_columns("COMMITTER_NAME", "AUTHOR_NAME")
        self.rename_columns("COMMITTER_TIMESTAMP", "TIMESTAMP")
        self.rename_columns("FILE_URL", "CONTENTS_URL")

    def merge_preprocessed_files(self, file, column_to_create_in_main_file):
        """
            The method merges the columns to create the final preprocessed dataframe.
            
            :param file: file to be merged
            :type file: str  
            
            :param column_to_create_in_main_file: column to be added
            :type column_to_create_in_main_file: str 
        """
        file_df = pd.read_csv(file)
        file_df = file_df.sort_values(by=["COMMIT_ID"], ascending=[True])
        self.github_data_dump_df = self.github_data_dump_df.sort_values(by=["COMMIT_ID"], ascending=[True])
        self.github_data_dump_df[column_to_create_in_main_file] = file_df[column_to_create_in_main_file]

    def save_preprocessed_file(self, file_name):
        """
            The method writes the dataframe as csv
            
            :param file_name: file path
            :type file_name: str  
        """
        self.github_data_dump_df.to_csv(f"{self.pre_processed_file_path}/{file_name}.csv", encoding='utf-8-sig',
                                        index=False)

    def save_preprocessed_file_as_csv_xlsx(self, file_name):
        """
            The method writes the dataframe as excel and modified the timestamo format
            
            :param file_name: file path
            :type file_name: str  
        """
        try:
            self.github_data_dump_df['TIMESTAMP'] = pd.to_datetime(self.github_data_dump_df['TIMESTAMP'],
                                                                   format='%Y-%m-%dT%H:%M:%S')
            writer = pd.ExcelWriter(f"{self.pre_processed_file_path}/{file_name}.xlsx", engine='xlsxwriter',
                                    datetime_format='%Y-%m-%dT%H:%M:%S', options={'strings_to_urls': False})
            self.github_data_dump_df.to_excel(writer, sheet_name='Sheet 1', index=False)
            writer.save()

            pd.read_excel(f"{self.pre_processed_file_path}/{file_name}.xlsx").to_csv(
                f"{self.file_path}/{file_name}.csv",
                encoding='utf-8-sig', index=False)
        except Exception as e:
            print(f"Exception {e}")

    def save_schedule_file(self):
        """
        The method creates directory with current date for each day's data collected and writes it to the 
        """
        current_date = datetime.today().strftime('%Y-%m-%d')
        CDPConfigValues.create_directory(f"{CDPConfigValues.schedule_file_path}/{self.project_name}/{current_date}")
        self.github_data_dump_df.to_csv(f"{CDPConfigValues.schedule_file_path}/{self.project_name}/"
                                        f"{current_date}/{CDPConfigValues.final_feature_file}", encoding='utf-8-sig',
                                        index=False)

    def update_fill_na(self, file_name):
        """
        The method fills the blank values for SUB_MODULE_STATS to 0
        """
        self.github_data_dump_df = pd.read_csv(
            f"{CDPConfigValues.preprocessed_file_path}/{self.project_name}/{file_name}")
        self.github_data_dump_df["SUB_MODULE_STATS"] = self.github_data_dump_df["SUB_MODULE_STATS"].fillna(0)

    @staticmethod
    def drop_additional_columns(file_df, column_name):
        try:
            file_df = file_df.drop(column_name, axis=1)
        except Exception as e:
            pass
            print(e)

        return file_df


def file_pre_process(project):
    preprocessor = Preprocessor(project)

    print("converting month day date hour to categorical")
    preprocessor.convert_month_day_date_hour_to_categorical()
    preprocessor.save_preprocessed_file("old_features_preprocessed_step0")

    print("converting file status to categorical")
    preprocessor.file_status_to_categorical()
    preprocessor.save_preprocessed_file("old_features_preprocessed_step1")

    print("determining commits as fix")
    preprocessor.determine_commit_is_fix()
    preprocessor.save_preprocessed_file("old_features_preprocessed_step2")

    print("Getting file size of a commit")
    preprocessor.get_file_size()
    preprocessor.save_preprocessed_file("old_features_preprocessed_step3")

    print("Getting file Commit age and Number of Developer")
    preprocessor.get_commit_file_age_and_number_of_developer_mp()
    preprocessor.save_preprocessed_file("old_features_preprocessed_step4")

    print("Getting Developer Experience")
    preprocessor.get_developer_experience_using_mp(True)
    preprocessor.save_preprocessed_file("old_features_preprocessed_step5")
    preprocessor.get_developer_experience_using_mp(False)
    preprocessor.save_preprocessed_file("old_features_preprocessed_step6")

    print("Getting Sub Module Stats")
    preprocessor.get_sub_module_stats()
    preprocessor.save_preprocessed_file("old_features_preprocessed_step7")

    print("Getting Developer Stats")
    preprocessor.get_developer_stats()
    preprocessor.save_preprocessed_file("old_features_preprocessed_step8")
    preprocessor.save_schedule_file()

    print("Dropping Unnecessary columns")
    preprocessor.drop_unnecessary_columns()
    preprocessor.save_preprocessed_file("old_features_preprocessed_step9")

    print("getting Unique Files per commit")
    preprocessor.get_no_of_files_count()
    preprocessor.save_preprocessed_file("old_features_preprocessed_step10")

    print("Separating File name and Directory")
    preprocessor.update_file_name_directory()
    preprocessor.save_preprocessed_file("old_features_preprocessed_step11")

    print("Getting Unique directories per commit..")
    preprocessor.get_no_of_directories_count()
    preprocessor.save_preprocessed_file("old_features_preprocessed_step12")

    preprocessor.rename()
    preprocessor.save_preprocessed_file("old_features_preprocessed_step13")
    print("Creating Final preprocessed cdp file")
    preprocessor.update_fill_na("old_features_preprocessed_step13.csv")
    preprocessor.save_preprocessed_file("old_features_preprocessed_step14")

# Test Method for validation
if __name__ == "__main__":

    for key in sorted(CDPConfigValues.cdp_projects.keys()):
        start_time = time.time()
        file_pre_process(key)
        end_time = time.time()
        print(f"Time Taken to complete Pre-processing {end_time - start_time}")
