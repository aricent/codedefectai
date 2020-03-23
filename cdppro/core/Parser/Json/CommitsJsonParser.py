import json
import re
import pandas as pd
from Parser.Json.IJsonParser import IJsonParser

class CommitsJsonParser(IJsonParser):
    """
    Parses data received from github commits API and gets below mentioned details about commit.
    commit_id, commit_message, author_name, timestamp, committer_email, file_name, file_status, lines_added,
    lines_modified, lines_deleted, nd, nf, files_entropy, and contents_url.
    """

    def __init__(self):
         """
        Class constructor
        :param commit_details: list to store bug Ids
        :type commit_details: list
        :param commit_list: bugs data DataFrame
        :type commit_list: Pandas Dataframe
        """
        super().__init__()
        self.commit_details = None
        self.commit_list = []

    def parse_id_listing(self, response_list):
        """
        helper method to find first level info from commit json.
        """
        shaList = list()

        for i in response_list:
            jsonResponse = json.loads(str(i))
            for firstLevelItems in jsonResponse:
                sha = firstLevelItems.get('sha')
                shaList.append(sha)

        return shaList

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

    def parse_json(self, res_json, cdp_dump_path):
        """
        method to parse json data and extract following information from it.
        commit_id, commit_message, author_name, timestamp, committer_email, file_name, file_status, lines_added,
        lines_modified, lines_deleted, nd, nf, files_entropy, and contents_url.
 
        :param res_json: json response received from github commits API 
        :type res_json:  str
        :param cdp_dump_path: path to save commits data in a file
        :type cdp_dump_path: str
        :returns: Commit Details dataframe after parsing json
        :rtype: Pandas Dataframe
        """
        files_list = list()
        additions_list = list()
        modifications_list = list()
        deletion_list = list()
        file_entropy = list()

        status_list = list()
        author_list = list()
        commit_list = list()
        no_of_directories_list = list()
        no_of_files_list = list()
        commit_message_list = list()
        timestamp_list = list()
        committer_email_list = list()
        content_url = list()

        self.commit_list = {
            "COMMIT_ID": [],
            "COMMIT_MESSAGE": [],
            "AUTHOR_NAME": [],
            "TIMESTAMP": [],
            "COMMITTER_EMAIL": [],
            "FILE_NAME": [],
            "FILE_STATUS": [],
            "LINES_ADDED": [],
            "LINES_MODIFIED": [],
            "LINES_DELETED": [],
            "ND": [],
            "NF": [],
            "FILES_ENTROPY": [],
            "CONTENTS_URL": []
        }

        for response_data in res_json:

            json_response = json.loads(response_data)

            commitID = json_response.get('sha')
            commit = json_response.get('commit')
            commit_message = commit.get("message")
            committer_arr = commit.get('committer')
            author_name = committer_arr.get('name')
            checkin_time = committer_arr.get('date')
            email = committer_arr.get('email')

            filesData = json_response.get('files')

            count = 0
            commit_file_list = list()
            entropy = list()
            for items in filesData:
                # print(items)
                count += 1
                commit_list.append(commitID)
                commit_message_list.append(commit_message)
                author_list.append(author_name)
                timestamp_list.append(checkin_time)
                committer_email_list.append(email)
                filename = items.get('filename')
                files_list.append(filename)
                commit_file_list.append(filename)
                url = items.get('contents_url')
                content_url.append(url)
                status = items.get('status')
                status_list.append(status)
                lines_add_or_modified = items.get('additions')
                lines_deleted = items.get('deletions')
                code_modified = items.get('patch')
                if code_modified is not None:
                    code_modified = len(re.findall(r'.*@@ (.*) @@.*', code_modified))
                else:
                    code_modified = 0
                if status == 'modified':
                    modifications_list.append(lines_add_or_modified)
                    additions_list.append(0)
                else:
                    additions_list.append(lines_add_or_modified)
                    modifications_list.append(0)
                deletion_list.append(lines_deleted)
                file_entropy.append(code_modified)
                entropy.append(code_modified)
            unique_directory = self.get_distinct_directory_count(commit_file_list)
            for i in range(count):
                no_of_directories_list.append(unique_directory)

            file_count = len(list(set(commit_file_list)))
            for i in range(count):
                no_of_files_list.append(file_count)

        self.commit_list['COMMIT_ID'] = commit_list
        self.commit_list['COMMIT_MESSAGE'] = commit_message_list
        self.commit_list['AUTHOR_NAME'] = author_list
        self.commit_list['TIMESTAMP'] = timestamp_list
        self.commit_list['COMMITTER_EMAIL'] = committer_email_list
        self.commit_list['FILE_NAME'] = files_list
        self.commit_list['FILE_STATUS'] = status_list
        self.commit_list['LINES_ADDED'] = additions_list
        self.commit_list['LINES_MODIFIED'] = modifications_list
        self.commit_list['LINES_DELETED'] = deletion_list
        self.commit_list["ND"] = no_of_directories_list
        self.commit_list["NF"] = no_of_files_list
        self.commit_list['FILES_ENTROPY'] = file_entropy
        self.commit_list['CONTENTS_URL'] = content_url

        self.commit_details = pd.DataFrame(self.commit_list)

        return self.commit_details
