import base64
import json
import time

import requests

from Utility.CDPConfigValues import CDPConfigValues


class WebConstants:
    """
        Class definition for storing constants for authorization,URL's , 
        Headers for data extraction and storage

    """
    # Prepare authentication GitHub Header
    github_base_url = "https://api.github.com/repos"
    counter = 0

    def __init__(self, project):

        self.project_name = CDPConfigValues.cdp_projects[project]

        self.commit_base_url = f"{WebConstants.github_base_url}/{self.project_name}/commits"
        self.commit_url_paginated = self.commit_base_url + "?page={0}&per_page=100"

        self.commit_details_url = self.commit_base_url + "/{0}"
        self.commit_file_history_url = self.commit_base_url + "?path={0}"

        self.issues_url = f"{WebConstants.github_base_url}/{self.project_name}/issues"
        bug_label = CDPConfigValues.configFetcher.get('bug_label', project)
        self.bug_url = self.issues_url + f"?labels={bug_label}" + "&&state=all&page={0}&per_page=100"

        self.event_url = self.issues_url + "/{0}/events?page=0&per_page=100"
        self.timeline_url = self.issues_url + "/{0}/timeline?page=0&per_page=100"

        self.file_size_url = f"{WebConstants.github_base_url}/{self.project_name}/git/trees/" + "{0}?recursive=1"

        self.contribution_url = f"{WebConstants.github_base_url}/{self.project_name}/contributors" + "?&page={}"
        self.contents_url = f"{WebConstants.github_base_url}/{self.project_name}/contents/" + "{0}?ref={1}"

        self.user_details_url = "https://api.github.com/users"
        self.user_password = ""
        self.header = ""

        self.headers = {}
        self.header_timer = {}

    def fetch_header(self, header_type=None):

        user_accounts = CDPConfigValues.github_username.split(",")
        user_accounts = list(map(str.strip, user_accounts))
        
        user_id = WebConstants.counter % len(user_accounts)
        WebConstants.counter = WebConstants.counter + 1
        githubPassword = CDPConfigValues.github_password
        githubUserName = user_accounts[user_id]
        encodedStr = githubUserName + ":" + githubPassword

        if self.headers.get(f"{githubUserName}_{header_type}") is None or (
                self.header_timer.get(f"{githubUserName}_{header_type}") is not None and
                (time.time() - self.header_timer[f"{githubUserName}_{header_type}"]) > 3600):

            self.header_timer[f"{githubUserName}_{header_type}"] = time.time()
            self.user_password = base64.standard_b64encode(encodedStr.encode()).decode("ascii")

            if header_type is None:
                self.header = {'Accept': 'application/vnd.github.symmetra-preview+json',
                                   'User-agent': 'Mozilla/5.0',
                                   'Authorization': 'Basic %s' % self.user_password}
            else:
                self.header = {'Accept': 'application/vnd.github.mockingbird-preview', 'User-agent': 'Mozilla/5.0',
                                   'Authorization': 'Basic %s' % self.user_password}

            print(f"header: {self.header}")

            self.headers[f"{githubUserName}_{header_type}"] = self.header
        else:
            return self.headers[f"{githubUserName}_{header_type}"]

        return self.header

    @staticmethod
    def fetch_proxy():

#        proxy_list = [
#            "165.225.104.34:80", "165.225.106.34:80"
#        ]
        proxy_list = CDPConfigValues.proxy_list.split(",")
        proxy_id = WebConstants.counter % len(proxy_list)
        return f"http://{proxy_list[proxy_id]}"


if __name__ == "__main__":
    # For testing purpose
    webConstants = WebConstants("project_1")
    webConstants.fetch_header()
    webConstants.fetch_header()
    webConstants.fetch_header()
    webConstants.fetch_header()
    webConstants.fetch_header()
