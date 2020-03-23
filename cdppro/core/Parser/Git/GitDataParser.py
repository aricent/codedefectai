import asyncio
import re
import traceback
from collections import defaultdict

import pandas as pd

from Utility.CDPConfigValues import CDPConfigValues
from Utility.WebConstants import WebConstants


class GitFile:
    """
    Class object used in get_file_status() method of GitParser class to 
    find if the file has been added, modified or deleted.
    """
    def __init__(self):
        """
        Class constructor
        :param file_name: name of file to be parsed
        :type file_name: str
        :param deleted_lines: number of lines deleted from file
        :type deleted_lines: int
        :param added_lines: number of lines added in file
        :type added_lines: int
        :param modified_lines: number of modified lines in file
        :type modified_lines: int
        :param file_status: whether file is added, modified or deleted
        :type file_status: str
        
        
        """
        self.file_name = None
        self.deleted_lines = 0
        self.added_lines = 0
        self.modified_lines = 0
        self.file_status = ""


class GitParser:
    """
    Parse git log for provided project and return the below information:
    commit id, commit message, author name, author email, author timestamp, 
    committer name, committer email, committer timestamp, file name, file status,
    lines added, lines modified, lines deleted, number of files, number of directories, files entropy, file url
    for every commit - filename combination.
    """

    def __init__(self, project, git_log, git_file_status, git_file_stats):
        """
        Class constructor
        :param project: unique project id of project to be parsed
        :type project: str
        :param git_log: unique project id of project to be parsed
        :type git_log: str
        :param git_file_status: unique project id of project to be parsed
        :type git_file_status: str
        :param git_file_stats: unique project id of project to be parsed
        :type git_file_stats: str
        
        :param project: unique project id of project to be parsed
        :type project: str
        :param project: unique project id of project to be parsed
        :type project: str
        :param project: unique project id of project to be parsed
        :type project: str
        :param project: unique project id of project to be parsed
        :type project: str
        :param project: unique project id of project to be parsed
        :type project: str
        
        """
        self.project_name = CDPConfigValues.configFetcher.get("name", project)
        self.web_connections = WebConstants(project)
        self.git_log = git_log
        self.git_file_status = git_file_status
        self.git_file_stats = git_file_stats

        self.commit_id = ""
        self.committer_message = ""

        self.author = ""
        self.author_email = ""
        self.committer = ""
        self.committer_email = ""

        self.author_timestamp = ""
        self.committer_timestamp = ""

        self.file_details = defaultdict(list)
        self.file_status = defaultdict(list)
        self.file_stats = defaultdict(list)

    @staticmethod
    def get_distinct_directory_count(file_list):
        """
        method to find number of unique directories modified in a commit
        :param file_list: list of file names to be processed
        :type file_list: list
        :return: unique directory count in a file
        :rtype: int
        """
        
        directory = list()
        for file in file_list:
            directory.append(file.split(file.split('/')[-1])[0])

        return len(set(directory))

    @staticmethod
    def get_file_status(file, file_status, file_stats):
        """
        method finds whether a file has been added, deleted or modified in commit.
        :param file: file name
        :type file: str
        :param file_status: Added modified or deleted
        :type file_status: str
        :param file_stats: number of lines added/ deleted
        :type file_stats: int
        :return: object of GitFile class.
        :rtype: object
        
        
        """
        git_file = GitFile()

        git_file.file_name = file

        git_file.deleted_lines = int(file_stats[1]) if file_stats[1] != "-" else 0

        if file_status == "A":
            git_file.file_status = "added"
            git_file.added_lines = int(file_stats[0]) if file_stats[0] != "-" else 0
        elif file_status == "M":
            git_file.file_status = "modified"
            git_file.modified_lines = int(file_stats[0]) if file_stats[0] != "-" else 0
        elif file_status == "R":
            git_file.file_status = "renamed"
            git_file.added_lines = int(file_stats[0]) if file_stats[0] != "-" else 0
        else:
            git_file.file_status = "removed"

        return git_file

    @staticmethod
    def write(file_name, content):
        """
        Helper Method
        """
        file = open(file_name, "w", encoding="utf-8", newline="\n")
        for line in content:
            file.write(line)
            file.write("\n")
        file.close()

    def write_git_log(self, file_name):
        """
        Helper Method
        """
        self.write(file_name, self.git_log)

    def write_git_status(self, file_name):
        """
        Helper Method
        """
        self.write(file_name, self.git_file_status)

    def write_git_stats(self, file_name):
        """
        Helper Method
        """
        self.write(file_name, self.git_file_stats)

    async def parser(self):
        """
        method parses git logs to extract details for one commit and then extracts
        details for each file in the commit. It returns below details about a commit:
        commit id, commit message, author name, author email, author timestamp, 
        committer name, committer email, committer timestamp, file name, file status,
        lines added, lines modified, lines deleted, number of files, number of directories, files entropy, and file url.
        :return : Pandas dataframe containing above mentioned information
        :rtype: Pandas Dataframe
        
        """

        file_names = list()
        file = ""
        counter = 0
        continue_to_loop = True
        commit_counter = 0
        status_counter = 1
        for line in self.git_log:
            status, stats = "", ""
            try:
                if line.startswith("Commit:"):
                    self.committer = line.split("Commit:")[1].split("<")[0]
                    self.committer_email = line.split("Commit:")[1].split("<")[1].split(">")[0]
                elif line.startswith("commit"):
                    self.commit_id = line.split("commit ")[1].split(" ")[0].strip()
                    if counter != 0:
                        break
                    commit_counter = commit_counter + 1
                elif line.startswith("Author:"):
                    self.author = line.split("Author:")[1].split("<")[0]
                    self.author_email = line.split("Author:")[1].split("<")[1].split(">")[0]

                elif line.startswith("AuthorDate:"):
                    self.author_timestamp = line.split("AuthorDate:")[1].strip()
                elif line.startswith("CommitDate:"):
                    self.committer_timestamp = line.split("CommitDate:")[1].strip()
                elif file == "" and not line.startswith("diff --"):
                    self.committer_message = self.committer_message + line
                elif line.startswith("diff --cc"):
                    file = line.split("diff --cc")[1].strip()
                    file_names.append(file)
                    if commit_counter == status_counter:
                        continue_to_loop = True
                elif line.startswith("diff --git a/"):
                    file = line.split(" b/")[1].strip()
                    file_names.append(file)
                    if commit_counter == status_counter:
                        continue_to_loop = True

                if file != "":

                    self.file_details[file].append(line)

                    if continue_to_loop and len(self.git_file_status) > counter and \
                            self.git_file_status[counter] is not None and self.git_file_status[counter] != "":

                        if self.git_file_status[counter].__contains__("commit "):
                            continue_to_loop = False
                            status_counter = status_counter + 1
                        else:
                            status = self.git_file_status[counter].split("\t")
                            if re.search("^R\d+", status[0]) is not None:
                                # noinspection PyTypeChecker
                                self.file_status[status[2].strip()] = 'R'
                            else:
                                self.file_status[status[1].strip()] = status[0]

                    if continue_to_loop and len(self.git_file_stats) > counter and \
                            self.git_file_stats[counter] is not None and self.git_file_stats[counter] != "":

                        stats = self.git_file_stats[counter].split("\t")
                        if self.git_file_stats[counter].__contains__("{"):
                            key = stats[2].split("{")[0].strip() + \
                                  stats[2].split("{")[1].split("}")[0].split("=> ")[1].strip() + \
                                  stats[2].split("{")[1].split("}")[1].strip()
                            key = key.replace("//", "/")
                        elif self.git_file_stats[counter].__contains__("=>"):
                            key = stats[2].split("=> ")[1].strip()
                            key = key.replace("//", "/")
                        else:
                            key = stats[2].strip()

                        self.file_stats[key] = [stats[0], stats[1]]

            except Exception as e:
                print(f"Exception Occurred for file {file} \n status - {status} \n stats - {stats}")
                print(traceback.print_tb(e.__traceback__))
                print("\n")

            counter = counter + 1

        number_of_files = len(set(file_names))
        number_of_directory = self.get_distinct_directory_count(file_names)
        result = list()

        base_content_url = self.web_connections.contents_url
        # "https://api.github.com/repos/spring-projects/spring-boot/contents/{0}?ref={1}"
        for file in self.file_status.keys():
            try:
                file_entropy = 0
                git_diff_counter = -1
                for line in self.file_details[file]:
                    if 0 == git_diff_counter:
                        file_entropy = file_entropy + len(re.findall(r'.*@@ (.*) @@.*', line))

                    elif line.startswith("diff --git") or line.startswith("diff --cc"):
                        git_diff_counter = git_diff_counter + 1

                content_url = base_content_url.format(file, self.commit_id)
                # print(file, self.file_status[file], self.file_stats[file])
                git_file = self.get_file_status(file, self.file_status[file], self.file_stats[file])

                result.append(
                    (self.commit_id, self.committer_message, self.author, self.author_email, self.author_timestamp,
                     self.committer, self.committer_email, self.committer_timestamp, file,
                     git_file.file_status, git_file.added_lines, git_file.modified_lines, git_file.deleted_lines,
                     number_of_files, number_of_directory, file_entropy, content_url))

            except Exception as e:
                print(f"Exception Occurred for file {file}")
                print(traceback.print_tb(e.__traceback__))
                print("\n")

        data_frame = pd.DataFrame(result, columns=["COMMIT_ID", "COMMIT_MESSAGE",
                                                   "AUTHOR_NAME", "AUTHOR_EMAIL", "AUTHOR_TIMESTAMP",
                                                   "COMMITTER_NAME", "COMMITTER_EMAIL", "COMMITTER_TIMESTAMP",
                                                   "FILE_NAME", "FILE_STATUS",
                                                   "LINES_ADDED", "LINES_MODIFIED", "LINES_DELETED",
                                                   "NF", "ND", "FILES_ENTROPY", "FILE_URL"])

        # data_frame.to_csv(f"{CDPConfigValues.git_command_csv_data_path}/{self.project_name}/{file_name}.csv",
        #                   index=False)
        await asyncio.sleep(0)

        return data_frame
