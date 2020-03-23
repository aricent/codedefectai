import json
from Parser.Json.IJsonParser import IJsonParser

class TimelineJsonParser(IJsonParser):
    """
    class to parse json returned by github timeline API
    """
    def __init__(self):
        super().__init__()

    def parse_id_listing(self, response_list):
        pass

    def parse_json(self, res_json, output_file_path):
        pass

    @staticmethod
    def parse_timeline(response):
        """
        function to parse github timeline API response and return pull request url.
        :param response: timeline API response
        :type response: str
        """
        json_response = json.loads(response)
        try:
            for data in json_response:
                event = data.get('event', None)
                # print(event)
                if event is not None and event == 'cross-referenced':
                    source_arr = data.get('source', None)
                    if source_arr is not None:
                        issue_arr = source_arr.get('issue', None)
                        if issue_arr is not None:
                            pull_request = issue_arr.get('pull_request', None)
                            if pull_request is not None:
                                pullUrl = pull_request.get('url', None)
                                return pullUrl
        except Exception as e:
            print(e)

        return None
