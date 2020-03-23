from abc import ABCMeta, abstractmethod

class IJsonParser:
    """
    Base class for BugsJsonParser, CommitsJsonParser, EventsJsonParser, 
    PullJsonParser and TimeLineJsonParser
    """
    def __init__(self):
        pass

    __metaclass__ = ABCMeta

    @classmethod
    def version(cls): return "1.0"

    @abstractmethod
    def parse_id_listing(self, response_list): raise NotImplementedError("This method needs to have a concrete \
                                                    implementation of the parse_id_listing method")

    """ 
    abstract method for implementing parsing logic for extracting data from Github projects 
    depending on the API and the json response.
    """

    @abstractmethod
    def parse_json(self, res_json, output_file_path): raise NotImplementedError("This method needs to have a concrete \
                                                    implementation of the parse_json method")
    """ 
    abstract method for implementing parsing logic for extracting data from Github projects 
    depending on the API and the json response.
    """