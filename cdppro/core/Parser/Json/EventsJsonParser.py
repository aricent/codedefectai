import json
import pandas as pd
from Parser.Json.IJsonParser import IJsonParser
from Parser.Json.PullJsonParser import PullJsonParser
from Parser.Json.TimelineJsonParser import TimelineJsonParser
from WebConnection.WebConnection import WebConnection


class EventsJsonParser(IJsonParser):
    """
    Parses data received from github events API and finds commit id where an issue was closed.
    """
    def parse_json(self, res_json, output_file_path):
        pass

    def parse_id_listing(self, response_list):
        pass

    def __init__(self):
        super().__init__()
        self.closed_event_data_frame = ""

    def find_buggy_commits_based_on_repository_fixes(self, web_constants, events_data_frame, file_path=None):
        """
        Parses data received from github events API and get below mentioned details
        commit_id, issue_id, create time(c_time) and update time(u_time).
        :param web_constants: object of WebConstants class
        :type web_constants: object
        :param events_data_frame: dataframe containing events details
        :type events_data_frame: Pandas Dataframe
        :param file_path: path to save events data in a file, default None
        :type file_path: str
        :returns: dataframe containing closed events data
        :rtype: Pandas Dataframe
        """
        web_connection = WebConnection()
        timeline_parser = TimelineJsonParser()
        pull_parser = PullJsonParser()
        timeline_url = str(web_constants.timeline_url)
        issue_id = ""
        list_commits = list()
        list_issues = list()
        list_timec = list()
        list_timeu = list()
        listtimeline_url = list()

        try:
            for index in events_data_frame.index:
                row = events_data_frame.loc[index]

                try:
                    json_response = json.loads(row['JSON_RESPONSE'])
                    issue_id = row['ISSUE_ID']

                    for items in json_response:
                        try:
                            event = items.get('event')
                            if event == 'closed':
                                commitID = items.get('commit_id')
                                if commitID is not None:
                                    list_commits.append(commitID)
                                    list_issues.append(issue_id)
                                    list_timec.append(row['CREATED_TIMESTAMP'])
                                    list_timeu.append(row['UPDATED_TIMESTAMP'])
                                    listtimeline_url.append("")
                                    break
                                else:
                                    newUrl = timeline_url.format(issue_id)
                                    listtimeline_url.append(newUrl)
                                    print(newUrl)
                                    header = web_constants.fetch_header(header_type="timeline")
                                    res = web_connection.get_rest_connection('GET', newUrl, header)
                                    pullurl = timeline_parser.parse_timeline(res)
                                    print(pullurl)
                                    if pullurl is not None:
                                        header = web_constants.fetch_header()
                                        pullRes = web_connection.get_rest_connection('GET', pullurl, header)
                                        sha = pull_parser.parse_pull_response(pullRes)
                                        list_commits.append(sha)
                                        list_issues.append(issue_id)
                                        list_timec.append(row['CREATED_TIMESTAMP'])
                                        list_timeu.append(row['UPDATED_TIMESTAMP'])
                        except Exception as e:
                            print("Failed in the inner most loop {}".format(e))
                except Exception as e:
                    print("Failed in outer loop {}".format(e))

        except Exception as e:
            print(e)
            print("Failed to fetch for issue id {}".format(issue_id))

        print(list_commits)
        self.closed_event_data_frame = pd.DataFrame(columns=['commitid', 'issue_id', 'c_time', 'u_time'])
        self.closed_event_data_frame['commitid'] = list_commits
        self.closed_event_data_frame['issue_id'] = list_issues
        self.closed_event_data_frame['c_time'] = list_timec
        self.closed_event_data_frame['u_time'] = list_timeu
        if file_path is not None:
            self.closed_event_data_frame.to_csv(file_path, encoding='utf-8-sig', index=False)

        return self.closed_event_data_frame

# if __name__ == "__main__":
