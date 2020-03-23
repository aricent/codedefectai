"""
Dir: VersionControl

"""

import asyncio
import os
import platform
import subprocess as sp
import time
import traceback
from collections import defaultdict
os.environ["GIT_PYTHON_REFRESH"] = "quiet"
import git
import pandas as pd

from Parser.Git.GitDataParser import GitParser
from Utility.CDPConfigValues import CDPConfigValues
from Utility.Utilities import Utilities


class GitData:
    """
        Class used to interact with github repo and extract the data specific to
        the project.
    """

    def __init__(self, project):
        self.project = project
        self.project_name = CDPConfigValues.configFetcher.get("name", project)
        self.friendly_name = CDPConfigValues.configFetcher.get("friendly_name", project)
        self.project_repo = CDPConfigValues.local_git_repo

    def clone_project(self, ):
        """
            Method used to clone github repository for a project.
        """

        log_status, log_error = "", ""
        if not os.path.exists(f"{CDPConfigValues.local_git_repo}/{self.project_name}") or not git.Repo(
                f"{CDPConfigValues.local_git_repo}/{self.project_name}").git_dir:
            command = ["git", "clone", CDPConfigValues.configFetcher.get("http", self.project)]
            query = sp.Popen(command, cwd=f"{CDPConfigValues.local_git_repo}", stdout=sp.PIPE, stderr=sp.PIPE)
            (log_status, log_error) = query.communicate()
        elif git.Repo(f"{CDPConfigValues.local_git_repo}/{self.project_name}").git_dir:
            command = ["git", "pull"]
            query = sp.Popen(command, cwd=f"{CDPConfigValues.local_git_repo}/{self.project_name}", stdout=sp.PIPE,
                             stderr=sp.PIPE)
            (log_status, log_error) = query.communicate()

        return f"{CDPConfigValues.local_git_repo}/{self.project_name}/"

    def get_all_commit_ids(self, ):
        """
            Method used to get commit ids from the github for a project.
        """
        commit_id = []
        self.clone_project()
        if platform.system().capitalize() == "Linux":
            command = f"git log | grep ^commit"
        else:
            command = f"git log | findstr /b commit"

        query = sp.Popen(command, cwd=f"{CDPConfigValues.local_git_repo}/{self.project_name}", stdout=sp.PIPE,
                         stderr=sp.PIPE, shell=True)
        (stdout, stderr) = query.communicate()
        if stdout != b'' or stderr == b'':
            stdout = stdout.decode("utf-8", errors='replace').split("\n")
            for line in stdout:
                if line != "":
                    commit_id.append(line.split(" ")[1])
        else:
            print(f"Git show command returned either empty or error for {commit_id}!!!")
            sdterr = stderr.decode("utf-8", errors='replace').split("\n")
            if sdterr != "":
                print(f"Git show command returned error for {commit_id}!!!\nError is \n {sdterr}")

        return commit_id

    def get_all_commit_ids_from_date(self, date):
        """
            Method used to get commit ids from the github for a project.
            
            #param date: Starting date, after that method will return the commit id.
            #type date: datetime
        """
        commit_id = []
        self.clone_project()
        print(f"Fetch Git Data from {date}")
        if platform.system().capitalize() == "Linux":
            command = f"git log --after='{date}' | grep ^commit"
        else:
            command = f"git log --after='{date}' | findstr /b commit"

        print(f"Git Command to execute {command}")

        query = sp.Popen(command, cwd=f"{CDPConfigValues.local_git_repo}/{self.project_name}", stdout=sp.PIPE,
                         stderr=sp.PIPE, shell=True)
        (stdout, stderr) = query.communicate()
        if stdout != b'' or stderr == b'':
            stdout = stdout.decode("utf-8", errors='replace').split("\n")
            for line in stdout:
                if line != "":
                    commit_id.append(line.split(" ")[1])
        else:
            print(f"Git show command returned either empty or error for {commit_id}!!!")
            sdterr = stderr.decode("utf-8", errors='replace').split("\n")
            if sdterr != "":
                print(f"Git show command returned error for {commit_id}!!!\nError is \n {sdterr}")

        return commit_id

    def get_commit_ids(self, days):
        """
            Method used to get commit ids from the github for a project.
        """
        commit_id = []
        self.clone_project()
        try:
            if platform.system().capitalize() == "Linux":
                command = f"git log --since={days}.day | grep ^commit"
            else:
                command = f"git log --since={days}.day | findstr /b commit"

            query = sp.Popen(command, cwd=f"{CDPConfigValues.local_git_repo}/{self.project_name}", stdout=sp.PIPE,
                             stderr=sp.PIPE, shell=True)
            (stdout, sdterr) = query.communicate()
            if stdout != b'' or sdterr == b'':
                stdout = stdout.decode("utf-8", errors='replace').split("\n")
                for line in stdout:
                    if line != "":
                        commit_id.append(line.split(" ")[1])

        except Exception as ex:
            print("Exception occurred....Closing database connections....")
            print(ex)

        return commit_id

    def create_git_log_from_api_to_csv(self, cdp_git_api_df, commit_id_list):
        """
            Utility method used to create csv file for the cdp github data.
            
            #param cdp_git_api_df: Dataframe containing cdp data.
            #type cdp_git_api_df: DataFrame
            
            #param commit_id_list: List of commit ids that has to saved in csv file.
            #type commit_id_list: list.
            
        """
        project_name = CDPConfigValues.configFetcher.get("name", self.project)
        for commit_id in commit_id_list:
            try:
                data_frame = cdp_git_api_df.loc[cdp_git_api_df["COMMIT_ID"] == commit_id]
                data_frame.to_csv(f"{CDPConfigValues.git_api_csv_data_path}/{project_name}/{commit_id}.csv",
                                  index=False)
            except Exception as e:
                print(f"Exception Occurred while saving git api csv file for Commit Id {commit_id}")
                print(traceback.print_tb(e.__traceback__))
                print("\n")

    async def run_command(self, *args):
        result = defaultdict()
        process = await asyncio.create_subprocess_exec(*args, cwd=self.project_repo, stdout=asyncio.subprocess.PIPE)

        stdout, stderr = await process.communicate()
        # print(stdout)
        if len(args) == 5:
            result["logs"] = (stdout, stderr)
        elif len(args) == 6 and args[5] == "--name-status":
            result["status"] = (stdout, stderr)
        elif len(args) == 6 and args[5] == "--numstat":
            result["stat"] = (stdout, stderr)

        return result

    async def get_git_data_async(self, commit_id):

        self.project_repo = f"{CDPConfigValues.local_git_repo}/{self.project_name}"

        result = await self.run_command(*["git", "show", "-m", commit_id, "--format=fuller"])
        git_log = result["logs"][0]
        git_log_error = result["logs"][1]

        result = await self.run_command(*["git", "show", "-m", commit_id, "--format=fuller", "--name-status"])
        git_status = result["status"][0]
        git_status_error = result["status"][1]

        result = await self.run_command(*["git", "show", "-m", commit_id, "--format=fuller", "--numstat"])
        git_stats = result["stat"][0]
        git_stats_error = result["stat"][1]

        git_data_frame = ""
        if git_log != b"" and git_status != b"" and git_stats != b"":
            git_parser = GitParser(self.project, git_log.decode("utf-8", errors='replace').split("\n"),
                                   git_status.decode("utf-8", errors='replace').split("\n"),
                                   git_stats.decode("utf-8", errors='replace').split("\n"))

            # git_parser.write_git_log(f"{CDPConfigValues.git_command_log_path}/{self.project_name}/{commit_id}.log")
            # git_parser.write_git_status(f"{CDPConfigValues.git_status_log_path}/{self.project_name}/{commit_id}.log")
            # git_parser.write_git_stats(f"{CDPConfigValues.git_stats_log_path}/{self.project_name}/{commit_id}.log")

            git_data_frame = await git_parser.parser()

        else:
            print(f"Git show command returned empty for {commit_id}!!!")
            if git_log_error != "":
                print(f"Git show command returned error for {commit_id}!!!\nError is \n {git_log_error}")
            if git_status_error != "":
                print(f"Git show command returned error for {commit_id}!!!\nError is \n {git_status_error}")
            if git_stats_error != "":
                print(f"Git show command returned error for {commit_id}!!!\nError is \n {git_stats_error}")

        await asyncio.sleep(0)

        return git_data_frame

    async def get_all_commits_async(self, commit_id_list):
        result = await asyncio.gather(
            *[self.get_git_data_async(commit_id) for commit_id in commit_id_list]
        )
        return result

    def get_all_commit_details(self, commit_list=None):
        """
            Utility method used to get commit details from the github for a project.
        """

        data_frame_from_git_command = pd.DataFrame(columns=["COMMIT_ID", "COMMIT_MESSAGE",
                                                            "AUTHOR_NAME", "AUTHOR_EMAIL", "AUTHOR_TIMESTAMP",
                                                            "COMMITTER_NAME", "COMMITTER_EMAIL", "COMMITTER_TIMESTAMP",
                                                            "FILE_NAME", "FILE_STATUS",
                                                            "LINES_ADDED", "LINES_MODIFIED", "LINES_DELETED",
                                                            "NF", "ND", "FILES_ENTROPY", "FILE_URL"])

        commit_file_path = f"{CDPConfigValues.cdp_dump_path}/{self.project_name}"

        project_path = f"{CDPConfigValues.local_git_repo}/{self.project_name}"
        CDPConfigValues.create_directory(project_path)

        git_command_csv_data = f"{CDPConfigValues.git_command_csv_data_path}/{self.project_name}"

        CDPConfigValues.create_directory(git_command_csv_data)
        CDPConfigValues.create_directory(f"{CDPConfigValues.git_command_log_path}/{self.project_name}")
        CDPConfigValues.create_directory(f"{CDPConfigValues.git_status_log_path}/{self.project_name}")
        CDPConfigValues.create_directory(f"{CDPConfigValues.git_stats_log_path}/{self.project_name}")

        start_time = time.time()
        if commit_list is None:
            commit_git_api_df = pd.read_csv(f"{commit_file_path}/{CDPConfigValues.commit_ids_file_name}")

            commit_git_api_df = commit_git_api_df["Commit_Ids"]
            commit_git_api_df = commit_git_api_df.drop_duplicates()

            commit_list = commit_git_api_df.to_list()

        print(f"Commit Ids to be Fetched {commit_list}")
        failed_commit_ids = commit_list

        if len(commit_list) != 0:
            loop_counter = 0

            while len(failed_commit_ids) != 0 and loop_counter < 10:

                loop_counter = loop_counter + 1

                commit_batches = list(
                    Utilities.create_batches(failed_commit_ids,
                                             batch_size=CDPConfigValues.git_command_execute_batch_size))
                total_batches = len(commit_batches)
                batch_counter, percent = 0, 0
                failed_commit_ids = list()

                print(f"Pre-processing Batch size {CDPConfigValues.git_command_execute_batch_size}")
                print(f"Total Batches to be executed is {total_batches}")

                for batch in commit_batches:
                    try:
                        loop = asyncio.new_event_loop()
                        # loop = asyncio.ProactorEventLoop()
                        asyncio.set_event_loop(loop)

                        if (total_batches * percent) // 100 == batch_counter:
                            print(
                                f"Total Batches completed is {batch_counter} "
                                f"and Failed batches Count is {len(failed_commit_ids)}")
                            percent = percent + 10

                        results_list = loop.run_until_complete(
                            self.get_all_commits_async(batch))
                        for result in results_list:
                            data_frame_from_git_command = pd.concat([data_frame_from_git_command, result],
                                                                    ignore_index=True)

                    except Exception as e:
                        print(f"Exception Occurred in get_all_commits !!!\n{traceback.print_tb(e.__traceback__)}")
                        for commit_id in batch:
                            failed_commit_ids.append(commit_id)

                    batch_counter = batch_counter + 1

            end_time = time.time()
            print(f"Time Taken Dev Experience {end_time - start_time}")

            data_frame_from_git_command['AUTHOR_TIMESTAMP'] = data_frame_from_git_command["AUTHOR_TIMESTAMP"].apply(
                lambda x: pd.Timestamp(x, tz="UTC"))

            data_frame_from_git_command['AUTHOR_TIMESTAMP'] = data_frame_from_git_command['AUTHOR_TIMESTAMP'].astype(
                str)

            data_frame_from_git_command['AUTHOR_TIMESTAMP'] = data_frame_from_git_command['AUTHOR_TIMESTAMP'].apply(
                lambda x: x[:-6])

            data_frame_from_git_command["COMMITTER_TIMESTAMP"] = data_frame_from_git_command[
                "COMMITTER_TIMESTAMP"].apply(
                lambda x: pd.Timestamp(x, tz="UTC"))

            data_frame_from_git_command['COMMITTER_TIMESTAMP'] = data_frame_from_git_command[
                'COMMITTER_TIMESTAMP'].astype(
                str)

            data_frame_from_git_command['COMMITTER_TIMESTAMP'] = data_frame_from_git_command[
                'COMMITTER_TIMESTAMP'].apply(
                lambda x: x[:-6])

        return data_frame_from_git_command


if __name__ == "__main__":
    git_data = GitData("project_2")
    git_data.clone_project()
    commit_ids = git_data.get_commit_ids(1)
    git_data.get_all_commit_details(commit_ids)
