import json
import pandas as pd
from Parser.Json.IJsonParser import IJsonParser


class BugsJsonParser(IJsonParser):
    """
    Class to parse bugs json data received from github APIs
    """

    def __init__(self):
        """
        Class constructor
        :param bug_list: list to store bug Ids
        :type bug_list: list
        :param bug_data_frame: bugs data DataFrame
        :type bug_data_frame: Pandas Dataframe
        """
        super().__init__()
        self.bug_list = ""
        self.bug_data_frame = ""
        

    def parse_id_listing(self, response_list):
        """
        method to parse json response and extract Id for each bug
        :param response_list: Bug data
        :type response_list: list
        """
        shaList = list()

        for i in response_list:
            jsonResponse = json.loads(str(i))
            for firstLevelItems in jsonResponse:
                sha = firstLevelItems.get('sha')
                shaList.append(sha)

        return shaList

    def parse_json(self, res_json, file_path=None):
        """
        method to parse json data and extract following information from it.
        issue_id, title, creator, assignee, state, created_timestamp, updated_timestamp, total_comments, labels.
        :param res_json: bugs data received from github APIs 
        :type res_json: Pandas Dataframe
        :param file_path: path to save bugs data in a file
        :type file_path: str
        """
        #        print ("Start of the data print !!!!!!!!!!!!!!!!!!!!!!")
        issue_list = list()
        title_list = list()
        creator_list = list()
        assignee_list = list()
        state_list = list()

        created_timestamp_list = list()
        updated_timestamp_list = list()
        total_comments_list = list()
        body_list = list()

        self.bug_list = {
            "ISSUE_ID": [],
            "TITLE": [],
            "CREATOR": [],
            "ASSIGNEE": [],
            "STATE": [],
            "CREATED_TIMESTAMP": [],
            "UPDATED_TIMESTAMP": [],
            "TOTAL_COMMENTS": [],
            "LABELS": []
        }

        outerLabelList = list()
        for responseData in res_json:
            # print(responseData)
            jsonResponse = json.loads(responseData)

            for items in jsonResponse:
                issueID = items.get('number', None)
                if issueID is not None:
                    issue_list.append(issueID)
                    #                print(issueID)
                    title = items.get('title')
                    title_list.append(title)
                    state = items.get('state')
                    state_list.append(state)
                    createTimestamp = items.get('created_at')
                    created_timestamp_list.append(createTimestamp)
                    updatedTimestamp = items.get('updated_at')
                    updated_timestamp_list.append(updatedTimestamp)
                    body = items.get('body')
                    body_list.append(body)
                    totalComments = items.get('comments')
                    total_comments_list.append(totalComments)
                    # print(body)
                    creatorData = items.get('user')

                    # print(creatorData)
                    creatorVal = creatorData.get('login')
                    creator_list.append(creatorVal)
                    assigneeData = items.get('assignee')
                    if assigneeData is not None:
                        #                    print(assigneeData)
                        assigneeVal = assigneeData.get('login')
                        assignee_list.append(assigneeVal)
                    else:
                        assignee_list.append('NA')

                    labelsList = list()

                    labelsData = items.get('labels')
                    for item in labelsData:
                        labelName = item.get('name')
                        # print(labelName)
                        if labelName.__contains__(": "):
                            label = labelName.split(' ')[1]
                        else:
                            label = labelName
                        labelsList.append(label)

                    outerLabelList.append(labelsList)

        self.bug_list['ISSUE_ID'] = issue_list
        self.bug_list['TITLE'] = title_list
        self.bug_list['CREATOR'] = creator_list
        self.bug_list['ASSIGNEE'] = assignee_list
        self.bug_list['STATE'] = state_list
        self.bug_list['CREATED_TIMESTAMP'] = created_timestamp_list
        self.bug_list['UPDATED_TIMESTAMP'] = updated_timestamp_list
        self.bug_list['TOTAL_COMMENTS'] = total_comments_list
        # self.bug_list['BODY'] = body_list
        self.bug_list['LABELS'] = outerLabelList
        self.bug_data_frame = pd.DataFrame(self.bug_list)
        if file_path is not None:
            self.bug_data_frame.to_csv(file_path, encoding='utf-8-sig', index=False)

        return self.bug_data_frame
