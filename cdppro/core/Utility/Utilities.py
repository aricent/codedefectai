class Utilities:
    def __init__(self):
        pass

    @staticmethod
    def create_batches(item_list, batch_size=4):
        for index in range(0, len(item_list), batch_size):
            yield item_list[index:index + batch_size]

    @staticmethod
    def create_url(url, url_param_list):
        url_list = [url + f"/{url_param}" for url_param in url_param_list]
        return url_list

    @staticmethod
    def format_url(url, items):
        url_list = [url.format(item) for item in items]
        return url_list
