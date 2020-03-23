import asyncio
import json
import os
import time
import traceback
from collections import defaultdict

import aiohttp
import pandas as pd
import urllib3

from Utility.CDPConfigValues import CDPConfigValues
from Utility.Utilities import Utilities

urllib3.disable_warnings()


class WebConnection:
    """
        Creates a restful URL connection by taking method, URL and headers 
        and returns the output as string value which can be a XML , json etc.
    """
    
    def __init__(self):
        self.proxy = ""
        self.header = ""
        
    def get_rest_connection(self, method, url, headers=None):

        if CDPConfigValues.use_proxy:
            http = urllib3.ProxyManager(self.proxy, maxsize=10)
        else:
            http = urllib3.PoolManager()

        response = http.request(method, url, headers=headers)
        page = response.data.decode('UTF-8')
        return str(page)

    @staticmethod
    def get_rest_connection_for_timeline(method, url, headers=None):

        http = urllib3.PoolManager()

        response = http.request(method, url, headers=headers)
        page = response.data.decode('UTF-8')
        return str(page)

    def paginated_json_str(self, method, paginated_url, headers):
        """
            Takes Paginated URL, headers and returns the string json list 
            object for all the pages.
        """
        
        current_page = 0
        page_length = 3
        json_list = list()
        while page_length > 2:
            github_url = paginated_url.format(current_page)
            print(github_url)

            # Method call for restful connection
            page = self.get_rest_connection(method, github_url, headers)
            json_list.append(str(page))
            page_length = len(page)
            current_page += 1

        return json_list

    def rest_response_list_for_id(self, method, url, headers, id_list):
        json_response = list()
        for index in id_list:
            url_local = url + '/' + index
            print(url_local)
            json_data = self.get_rest_connection(method, url_local, headers)
            json_response.append(json_data)

        return json_response

    
    async def fetch_and_store_result_wrt_index(self, session, index, url):
        """
           Code for parallel get requests, Fetching get requests and returning 
           the result having request numbers and send results as queue.
        """
        result = defaultdict()
        try:
            if CDPConfigValues.use_proxy:
                async with session.get(url, proxy=self.proxy) as response:
                    result[index] = (url, await response.text())
            else:
                async with session.get(url) as response:
                    result[index] = (url, await response.text())
        except Exception as e:
            results = (f"url:{url}", e)
            result[index] = Exception(f"Exception {results}")

        return result

    async def fetch_all_wrt_index(self, url_list, loop):
        async with aiohttp.ClientSession(loop=loop, headers=self.header) as session:
            results = await asyncio.gather(
                *[self.fetch_and_store_result_wrt_index(session, index, url) for index, url in enumerate(url_list)],
                return_exceptions=True)

            results_dictionary = defaultdict()

            for result in results:
                for key, value in result.items():
                    results_dictionary[key] = value

            results = []
            for key in sorted(results_dictionary.keys()):
                results.append(results_dictionary[key])

            return results

    async def fetch(self, session, url):
        try:
            if CDPConfigValues.use_proxy:
                async with session.get(url, proxy=self.proxy) as response:
                    result = (url, await response.text())
            else:
                async with session.get(url) as response:
                    result = (url, await response.text())
        except Exception as e:
            results = (f"url:{url}", e)
            raise Exception(f"Exception {results}")

        return result

    async def fetch_all(self, url_list, loop):
        async with aiohttp.ClientSession(loop=loop, headers=self.header) as session:
            results = await asyncio.gather(
                *[self.fetch(session, url) for url in url_list],
                return_exceptions=True)
            return results

    def get_async_data_using_asyncio_paginated(self, url, web_constant, batch_size=4):

        current_page, page_counter = 0, 0
        continue_loop = True
        results, failed_page_list, url_list, exception_list = list(), list(), list(), list()

        print(f"Url batch size {batch_size}")
        url_page_list = ""
        batch_timer = time.time()
        request_counter = 0
        while continue_loop:
            try:
                request_counter = request_counter + len(url_page_list)
                current_time = time.time()
                while request_counter > 80 and (batch_timer - current_time) < 60:
                    current_time = time.time()
                    time.sleep(1)
                else:
                    if batch_timer - current_time > 60:
                        batch_timer = time.time()
                        request_counter = 0

                loop = asyncio.get_event_loop()
                # loop = asyncio.ProactorEventLoop()
                asyncio.set_event_loop(loop)

                url_page_list = [url.format(page_number) for page_number in
                                 range(current_page, current_page + batch_size, 1)]

                self.header = web_constant.fetch_header()
                self.proxy = web_constant.fetch_proxy()
                results_list = loop.run_until_complete(self.fetch_all(url_page_list, loop))
                for result in results_list:
                    if isinstance(result, Exception):
                        print(f"Exception : {result}")
                        url_list.append(str(result).split(',')[0].split("url:")[1].replace("'", ""))
                    elif result is None:
                        raise Exception(url_page_list)
                    elif result[1] == '[]':
                        continue_loop = False
                        print(f"No Commit Data found for the page : {result[0]}")
                    elif '"message":"API rate limit exceeded for user ID' in result[1]:
                        url_list.append(result[0])
                    else:
                        results.append(result[1])
            except Exception as e:
                print(" Exception occurred in get_async_data_using_asyncio_paginated !!!")
                for url in url_page_list:
                    url_list.append(url)
                exception_list.append(e)
                print(f"Exception Occurred for page {current_page}!!! Execution is halted for 2 Seconds")
                time.sleep(2)

            if continue_loop:
                current_page = current_page + batch_size
                print(f"Total batches executed is {page_counter} and Total Failed Url batch is {len(url_list)}")

            page_counter = page_counter + 1

        if len(url_list) > 0:
            url_list = list(set(url_list))
            loop_counter = 0
            while len(url_list) > 0:
                loop_counter = loop_counter + 1
                print("Re-trying failed URL list")
                print(f"Sleeping for {60 * loop_counter} Seconds in get_file_size ...")
                time.sleep(60 * loop_counter)
                result = self.get_async_data_using_asyncio(url_list, web_constant, 5)
                url_list = list(set(result[0]))
                if len(result[1]) > 0:
                    results = results + result[1]

        print(f"Total Url's Requested is {current_page + batch_size}")

        return results

    """ fetches the http get results in batch wise without pagination"""

    def get_async_data_using_asyncio(self, url_list, web_constant, batch_size=4):

        results, failed_url_list, exception_list = list(), list(), list()
        batch_counter, percent = 0, 0
        batches = list(Utilities.create_batches(url_list, batch_size))
        total_batches = len(batches)
        print(f"Total Batches to be executed is {total_batches}")
        batch_timer = time.time()
        request_counter = 0
        for batch in batches:
            try:
                request_counter = request_counter + len(batch)
                current_time = time.time()
                time.sleep(1)
                while request_counter > 160 and (current_time - batch_timer) < 60:
                    current_time = time.time()
                    time.sleep(2)
                else:
                    if (current_time - batch_timer) > 60:
                        batch_timer = time.time()
                        request_counter = 0

                loop = asyncio.get_event_loop()
                asyncio.set_event_loop(loop)

                self.header = web_constant.fetch_header()
                self.proxy = web_constant.fetch_proxy()
                if (total_batches * percent) // 100 == batch_counter:
                    print(f"Total Batches completed is {batch_counter} and Failed Urls Count is {len(failed_url_list)}")
                    percent = percent + 10

                results_list = loop.run_until_complete(self.fetch_all(batch, loop))
                for result in results_list:
                    if isinstance(result, Exception):
                        print(f"Exception : {result}")
                        failed_url_list.append(str(result).split(',')[0].split("url:")[1].replace("'", ""))
                    elif result is None:
                        raise Exception(batch)
                    elif results is not None and (result[1] is None or result[1] == '[]'):
                        print(f"No Commit Details found for commit Id {result[0]} - {result[1]}")
                    elif '"message":"API rate limit exceeded for user ID' in result[1] or \
                            '"message":"API rate limit exceeded for user ID' in result or \
                            '"message": "Server Error"' in result[1]:
                        failed_url_list.append(result[0])
                    else:
                        if "Server Error" in result[1]:
                            print(f"url : {result[0]} and result -- {result[1]}")
                            failed_url_list.append(result[0])
                        else:
                            url = result[0].split("/events")[0].split("/")[-1]
                            results.append((url, result[1]))
                batch_counter = batch_counter + 1
            except Exception as e:
                for url in batch:
                    failed_url_list.append(url)
                exception_list.append(e)
                print(f"Exception Occurred for batch {batch_counter}!!! Execution is halted for 2 Seconds")
                time.sleep(2)

        print(exception_list)
        if len(failed_url_list) > 0:
            failed_url_list = list(set(failed_url_list))

        print(f"Total Url's Requested is {len(url_list)}")
        print(f"Total Url's Failed is {len(failed_url_list)}")

        async_result = (results, failed_url_list)
        return async_result

    def get_async_file_size(self, url_list, github_data_dump_df, web_constant, batch_size=4):

        CDPConfigValues.create_directory(
            f"{CDPConfigValues.preprocessed_file_path}/{web_constant.project_name}/file_size/")
        github_data_dump_df = github_data_dump_df.sort_values(by=["COMMITTER_TIMESTAMP"], ascending=[True])

        results, failed_url_list = list(), list()
        previous_commit_id = ""
        batch_counter = 0
        batches = list(Utilities.create_batches(url_list, batch_size))
        total_batches = len(batches)
        print(f"Total Batches to be executed is {total_batches}")
        percent = 0
        batch_timer = time.time()
        request_counter = 0
        previous_file_df = pd.DataFrame()
        for batch in batches:
            try:
                request_counter = request_counter + len(batch)
                current_time = time.time()
                time.sleep(1)
                while request_counter > 200 and (current_time - batch_timer) < 60:
                    current_time = time.time()
                    time.sleep(1)
                else:
                    if (current_time - batch_timer) > 60:
                        batch_timer = time.time()
                        request_counter = 0

                loop = asyncio.get_event_loop()
                # loop = asyncio.ProactorEventLoop()
                asyncio.set_event_loop(loop)
                self.header = web_constant.fetch_header()
                self.proxy = web_constant.fetch_proxy()

                if (total_batches * percent) // 100 == batch_counter:
                    print(f"Total Batches completed is {batch_counter} and Failed Urls Count is {len(failed_url_list)}")
                    percent = percent + 10

                batch_counter = batch_counter + 1

                results_list = loop.run_until_complete(self.fetch_all_wrt_index(batch, loop))
                results_list.sort()
                for result in results_list:
                    if isinstance(result, Exception):
                        url = str(result).split(',')[0].split("url:")[1].replace("'", "")
                        print(f"Exception : {result}\n {url}")
                        failed_url_list.append(url)
                    elif result is None:
                        raise Exception(batch)
                    elif result[1] is None or result[1] == '[]':
                        print(f"File Size Json is Empty {result[0]} - {result[1]}")
                    elif '"message":"API rate limit exceeded for user ID' in result[1] or \
                            '"message":"API rate limit exceeded for user ID' in result or \
                            '"message": "Server Error"' in result[1]:
                        failed_url_list.append(result[0])
                    else:
                        if "Server Error" in result[1]:
                            print(f"url : {result[0]} and result -- {result[1]}")
                            failed_url_list.append(result[0])
                        else:
                            commit_id = result[0].split('?')[0].split('/')[-1]
                            tree = json.loads(result[1]).get('tree', None)
                            file_size_df = pd.DataFrame.from_dict(tree)
                            file_list = github_data_dump_df.loc[github_data_dump_df["COMMIT_ID"] == commit_id][
                                "FILE_NAME"].drop_duplicates().to_list()

                            for file_name in file_list:
                                values = file_size_df.loc[file_size_df["path"] == file_name]["size"].values
                                if len(values) == 1:
                                    file_size = int(values[0])
                                    results.append((commit_id, file_name, file_size))

                                elif len(values) == 0:
                                    if previous_file_df is None:
                                        timestamp = \
                                            github_data_dump_df.loc[github_data_dump_df["COMMIT_ID"] == commit_id][
                                                "COMMITTER_TIMESTAMP"].to_list()[0]
                                        timestamp = \
                                            github_data_dump_df.loc[
                                                github_data_dump_df["COMMITTER_TIMESTAMP"] < timestamp][
                                                "COMMITTER_TIMESTAMP"].to_list()[-1]
                                        commit = \
                                            github_data_dump_df.loc[
                                                github_data_dump_df["COMMITTER_TIMESTAMP"] == timestamp][
                                                "COMMIT_ID"].values[0]

                                        if os.path.exists(
                                                f"{CDPConfigValues.preprocessed_file_path}/{web_constant.project_name}/file_size/{commit}.csv"):
                                            previous_file_df = pd.read_csv(
                                                f"{CDPConfigValues.preprocessed_file_path}/{web_constant.project_name}/file_size/{commit}.csv")

                                    if previous_file_df is None or len(previous_file_df) == 0:
                                        results.append((commit_id, file_name, 0))
                                    else:
                                        values = previous_file_df.loc[previous_file_df["path"] == file_name][
                                            "size"].values
                                        if len(values) == 0:
                                            results.append((commit_id, file_name, 0))
                                        else:
                                            file_size = int(values[0])
                                            results.append((commit_id, file_name, file_size))

                                elif len(values) > 1:
                                    results.append((commit_id, file_name, values[0]))
                                    print(f"file_name -- {file_name}, values -- {values}")

                                previous_file_df = file_size_df
                                previous_commit_id = commit_id

            except Exception as e:
                previous_file_df.to_csv(
                    f"{CDPConfigValues.preprocessed_file_path}/{web_constant.project_name}/file_size/{previous_commit_id}.csv", index=False)
                for url in batch:
                    failed_url_list.append(url)
                print(f"Exception Occurred for batch {batch_counter}!!! Execution is halted for 2 Seconds")
                print(f"Exception Occurred!!!\n{traceback.print_tb(e.__traceback__)}")
                time.sleep(2)

        failed_url_list = list(set(failed_url_list))

        print(f"Total Url's Requested is {len(url_list)}")
        print(f"Total Url's Failed is {len(failed_url_list)}")

        async_result = (results, failed_url_list)
        return async_result
