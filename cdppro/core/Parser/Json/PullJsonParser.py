import json
from Parser.Json.IJsonParser import IJsonParser

class PullJsonParser(IJsonParser):
    """
    class to pass pull github API reponse.
    """

    def __init__(self):
        super().__init__()

    def parse_id_listing(self, response_list):
        pass

    def parse_json(self, res_json, output_file_path):
        pass

    @staticmethod
    def parse_pull_response(response):
        """
        function to parse pull API resonse and return merge_commit_sha
        :param response: pull API response
        :type response: str
        :return: merge commit id
        :rtype: str
        """
        jsonResponse = json.loads(response)
        event = jsonResponse.get('state', None)
        if event is not None and event == 'closed':
            sha = jsonResponse.get('merge_commit_sha', None)
            return sha
