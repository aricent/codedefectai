import ast
import os

from Utility.ConfigFetcher import ConfigFetcher

cwd = os.path.realpath(os.path.curdir)
config_file = os.path.realpath(f"/cdpscheduler/Config/cdp.ini")


class CDPConfigValues:
    """
        Class used to setup configuration parameters.
    """
    @classmethod
    def reload(cls):
        global configFetcher
        configFetcher = ConfigFetcher(config_file)
        """ Fetching Scheduler Configuration"""
        CDPConfigValues.cdp_projects = configFetcher.get_projects("cdp_projects")

    @staticmethod
    def create_directory(directory: str):
        if not os.path.exists(directory):
            os.makedirs(directory)

    configFetcher = ConfigFetcher(config_file)
    cdp_log_path = configFetcher.get("cdp_log_path")
    create_directory.__func__(cdp_log_path)
    github_data_path = configFetcher.get("github_data_path")
    create_directory.__func__(github_data_path)
    cdp_dump_path = github_data_path + configFetcher.get('cdp_dump')
    create_directory.__func__(cdp_dump_path)
    preprocessed_file_path = github_data_path + configFetcher.get('preprocessed_file')
    create_directory.__func__(preprocessed_file_path)
    schedule_file_path = github_data_path + configFetcher.get('schedule_file')
    create_directory.__func__(schedule_file_path)

    local_git_repo = configFetcher.get('local_git_repo')
    create_directory.__func__(local_git_repo)
    git_command_root_path = github_data_path + configFetcher.get("git_command")
    create_directory.__func__(git_command_root_path)
    git_api_csv_data_path = github_data_path + configFetcher.get("git_api_csv_data")
    create_directory.__func__(git_api_csv_data_path)
    git_command_csv_data_path = github_data_path + configFetcher.get("git_command_csv_data")
    create_directory.__func__(git_command_csv_data_path)
    git_command_log_path = github_data_path + configFetcher.get("git_command_log")
    create_directory.__func__(git_command_log_path)
    git_stats_log_path = github_data_path + configFetcher.get("git_stats_log")
    create_directory.__func__(git_stats_log_path)
    git_status_log_path = github_data_path + configFetcher.get("git_status_log")
    create_directory.__func__(git_status_log_path)

    use_git_command_to_fetch_commit_details = \
        ast.literal_eval(configFetcher.get("use_git_command_to_fetch_commit_details"))
    save_api_data_in_csv = ast.literal_eval(configFetcher.get("save_api_data_in_csv"))
    save_command_data_in_csv = ast.literal_eval(configFetcher.get("save_command_data_in_csv"))

    commit_ids_file_name = configFetcher.get("commit_ids_file_name")
    commit_details_file_name = configFetcher.get("commit_details_file_name")
    final_feature_file = configFetcher.get("final_feature_file")
    commit_ids_having_missing_files = configFetcher.get("commit_ids_having_missing_files")
    commit_details_from_git_command = configFetcher.get("commit_details_from_git_command")
    commit_details_before_merging_with_command_data = \
        configFetcher.get("commit_details_before_merging_with_command_data")

    project_issue_list_file_name = configFetcher.get("project_issue_list_file_name")
    closed_events_list_file_name = configFetcher.get("closed_events_list_file_name")
    github_events_cdp_dump = configFetcher.get("github_events_cdp_dump")
    intermediate_file = configFetcher.get("intermediate_file")

    """ Fetching Database configuration """
    host = configFetcher.get("host", "database_config")
    port = configFetcher.get("port", "database_config")
    database = configFetcher.get("database", "database_config")
    username = configFetcher.get("username", "database_config")
    password = configFetcher.get("password", "database_config")

    """ Fetching API Configurations """
    use_proxy = ast.literal_eval(configFetcher.get("use_proxy", "cdp_api_config"))
    proxy_urls = configFetcher.get("proxy_url", "cdp_api_config").split(",")
    git_api_batch_size = int(configFetcher.get("git_api_batch_size", "cdp_api_config"))
    git_command_execute_batch_size = int(configFetcher.get("git_command_execute_batch_size", "cdp_api_config"))
    
    """ Fetching github configuration """
    github_username = configFetcher.get("username", "github_user_config")
    github_password = configFetcher.get("password", "github_user_config")
    proxy_list = configFetcher.get("proxy_list", "github_user_config")

    cdp_projects = configFetcher.get_projects("cdp_projects")

    def __init__(self):
        pass


if __name__ == "__main__":
    print(CDPConfigValues.cdp_log_path)
    print(CDPConfigValues.github_data_path)
    print(CDPConfigValues.cdp_dump_path)
    print(CDPConfigValues.git_api_csv_data_path)
    print(CDPConfigValues.git_command_csv_data_path)
    print(CDPConfigValues.git_command_log_path)
    print(CDPConfigValues.git_stats_log_path)
    print(CDPConfigValues.git_status_log_path)
    print(CDPConfigValues.cdp_projects)
