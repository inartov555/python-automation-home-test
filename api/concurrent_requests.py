"""
    @author iurii.nartov@xperi.com
    @created Apr-05-2023
"""

import os
import threading
import time

from tools.logger.logger import Logger


class ConcurrentRequests:
    """
    This class fits best for methods that make multiple requests in a line to make it faster.
    E.g. mind_api.open_api.open_api.ServiceOpenAPI#get_grid_row_search() makes a lot of
    /preview/offer requests etc.

    Notes:
        1. grequests library doesn't work in UTAF at the moment due to ssl and a few other libs
           but we need to use it instead of requests when it starts working.
           https://pypi.org/project/grequests/

        2. https://jira.xperi.com/browse/PARTDEFECT-17038
           Consider behavior in prod related to restricted number of v1/preview/offer requests per 5 minutes,
           currently running requests in parallel is disabled due to this specific prod configuration
           (/preview/offer service becomes unavailable in prod when number of requests reaches the limit)

    Usage:
        concur_req = ConcurrentRequests()
        concur_req.run_request_in_a_thread(GuideCellIocContainer.make_request, **kwargs_for_make_request_function)
        concur_req.get_response(thread_id)  # where thread_id may be 0, 1, 2...
        # Also, we need to check if some of requests failed
        concur_req.get_request_error(thread_id)
        # You can also get all request errors separated by '\n'
        concur_req.all_request_errors
        concur_req.get_request_params(thread_id)
        # Total number of made requests, if needed
        concur_req.total_number_of_requests

    Preserves order the requests were started with
    """

    class ReqThread(threading.Thread):

        def __init__(self, thread_id, req_function, **kwargs):
            """
            Args:
                thread_id (int): unique thread id
                req_function (function): a function that makes a request

            kwargs: input params needed for making a request
            """
            super().__init__()
            self.__log = Logger(__name__)
            self.__response = {}
            self.__request_error = None  # becomes not None only if request actually failed
            self.__thread_id = thread_id
            self.__req_function = req_function
            self.__kwargs = kwargs

        def run(self):
            try:
                self.__response = self.__req_function(**self.__kwargs)
            except Exception as ex:
                self.__request_error = ex

        @property
        def response(self):
            return self.__response

        @property
        def thread_id(self):
            return self.__thread_id

        @property
        def request_error(self):
            return self.__request_error

        @property
        def request_params(self):
            return self.__kwargs

    class SingleReq(ReqThread):
        """
        Object to make request in single thread.
        """
        def __init__(self, thread_id, req_function, **kwargs):
            """
            Args:
                thread_id (int): unique thread id
                req_function (function): a function that makes a request

            kwargs: input params needed for making a request
            """
            super().__init__(thread_id, req_function, **kwargs)
            self.__log = Logger(__name__)

        def start(self):
            self.run()

        def join(self):
            pass

    def __init__(self):
        self.__log = Logger(__name__)
        self.__thread_list = []  # [ReqThread] or [SingleReq]

    def _get_unique_thread_id(self):
        """
        Getting unique thread id. Starts from 1.

        Returns:
            int
        """
        return len(self.__thread_list)

    def _wait_till_all_responses_are_received(self):
        for thread_obj in self.__thread_list:
            thread_obj.join()

    def run_request_in_a_thread(self, req_function, pause=None, **kwargs):
        """
        Args:
            req_function (function): a function that makes a request
            pause (float): minimal pause between threads for the service to return the data

        kwargs: input params needed for making a request
        """
        threads_limit = os.getenv("MIND_MAX_THREADS", "1")
        pause = pause or float(os.getenv("MIND_THREADS_HOLDTIME", 1))
        if threads_limit == 'inf':
            req_method = self.ReqThread
        else:
            req_method = self.SingleReq
        thread1 = req_method(self._get_unique_thread_id(), req_function, **kwargs)
        self.__thread_list.append(thread1)
        thread1.start()
        time.sleep(pause)

    def get_request_error(self, thread_id):
        """
        Getting error of particular failed request by thread_id

        Args:
            thread_id (int): id of particular request thread

        Returns:
            str, if thread_id was passed
            None, if request did not fail
        """
        result = None
        self._wait_till_all_responses_are_received()
        for thread_obj in self.__thread_list:
            if thread_id == thread_obj.thread_id:
                result = thread_obj.request_error
        return result

    def get_response(self, thread_id):
        """
        Getting items dict

        Args:
            thread_id (int): thread id/orequest id to get particular response

        Returns:
            json, if thread_id was passed
            None, if thread wasn't found by id or request returned empty response
        """
        self._wait_till_all_responses_are_received()
        result = None
        for thread_obj in self.__thread_list:
            if thread_id == thread_obj.thread_id:
                result = thread_obj.response
        return result

    def get_request_params(self, thread_id):
        """
        Getting request params for passed request id

        Args:
            thread_id (int): id to get request params for particular request

        Returns:
            dict, params if thread_id was passed
            None, if thread wasn't found by id
        """
        self._wait_till_all_responses_are_received()
        result = None
        for thread_obj in self.__thread_list:
            if thread_id == thread_obj.thread_id:
                result = thread_obj.request_params
        return result

    @property
    def all_request_errors(self):
        """
        Getting errors of all requests in one line separated by '\n' character

        Returns:
            str, if there are failed requests
            None, if no failed requests
        """
        result = ""
        self._wait_till_all_responses_are_received()
        for index in range(len(self.__thread_list)):
            if self.get_request_error(index):
                result += f"\n ({index}) Request params: " + str(self.get_request_params(index)) + \
                    f"\n ({index}) Error: " + str(self.get_request_error(index))
        return result if result else None

    @property
    def total_number_of_requests(self):
        return len(self.__thread_list)
