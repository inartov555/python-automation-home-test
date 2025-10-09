"""
API methods
"""

from python_pytest_selenium_web_api_test.tools.logger.logger import Logger
from python_pytest_selenium_web_api_test.api.api.api_base import ApiJsonRequest


log = Logger(__name__)


class PublicApi(ApiJsonRequest):
    """
    API methods
    """

    def __init__(self):
        super().__init__("https", "catfact.ninja", "443")

    def get_facts(self, page=None, limit=None):
        """
        /facts

        Returns:
            dict
        """
        query_params = {}
        if page is not None:
            query_params["page"] = page
        if limit is not None:
            query_params["limit"] = limit
        resp = self.make_request("get", "/facts", {}, query_params, {})
        return resp

    def get_breeds(self):
        """
        /breeds

        Returns:
            dict
        """
        resp = self.make_request("get", "/breeds", {}, {}, {})
        return resp
