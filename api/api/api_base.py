import json
import requests
import time
from pprint import pformat
from requests import Response

from tools.logger.logger import Logger


log = Logger(__name__)


class ApiError(Exception):
    def __init__(self, error_msg):
        msg = "Failed to make request: {}".format(error_msg)
        super().__init__(msg)


class ApiBase:
    BEGIN_REQ = "========== BEGIN =========="
    END_REQ = "========== END =========="

    def __init__(self, protocol, host, port):
        self._unique_request_id_increment = 0
        self.protocol = protocol
        self.host = host
        self.port = port
        self.headers = {"User-Agent": "python-automation-home-test",
                        "Unique-RequestId": str(self._unique_request_id_increment) + "_" + hex(int(time.time()))}

    def append_headers(self, new_headers):
        """
        Args:
            new_headers (dict): new headers to append
        """
        self.headers.update(new_headers)

    def make_request(self, method, uri, payload={}, query_params={}, headers={}):
        """
        Getting the Response object.
        Log lines are consolidated into single variable to support concurrent requests, if any are added.

        Args:
            method (str): one of ("get", "post", "put", "delete")
            uri (str): e.g. /v1/someApiRequest
            payload (dict): payload
            query_params (dict): these params will be used in URL
            headers (dict): headers to add to the default ones

        Returns:
            Response
        """
        client = requests.session()
        url = '%s://%s:%s%s' % (self.protocol, self.host, self.port, uri)
        if headers:
            self.headers.update(headers)
        self._unique_request_id_increment += 1
        method = method.upper()
        methods_config = {}
        resp = Response()
        try:
            methods_config = {"GET": {"method": method,
                                      "url": url,
                                      "headers": self.headers,
                                      "params": query_params,
                                      "data": {},
                                      "timeout": 30,
                                      "verify": True,
                                      },
                              "POST": {"method": method,
                                       "url": url,
                                       "headers": self.headers,
                                       "params": query_params,
                                       "data": payload,
                                       "timeout": 30,
                                       "verify": True,
                                       },
                              "DELETE": {"method": method,
                                         "url": url,
                                         "headers": self.headers,
                                         "params": query_params,
                                         "data": payload,
                                         "timeout": 30,
                                         "verify": True,
                                         },
                              "PUT": {"method": method,
                                      "url": url,
                                      "headers": self.headers,
                                      "params": query_params,
                                      "data": payload,
                                      "timeout": 30,
                                      "verify": True,
                                      },
                              }
        except Exception as ex:
            message = "\n{}".format(self.BEGIN_REQ)
            message += "\nURL: {} \nMethod: {} \nheaders: {} \nparams: {} \npayload: {}".format(
                url, method, pformat(self.headers), query_params, payload)
            message += "\nError: {}".format(ex)
            message += "\n{}".format(self.END_REQ)
            log.error(message)
            raise ApiError(message)
        if method in methods_config.keys():
            message = "\n{}".format(self.BEGIN_REQ)
            message += "\nRequest config: {}".format(methods_config[method])
            try:
                resp = client.request(**methods_config[method])
                message += "\nResponse URL: {}".format(resp.url)
                message += "\nResponse text: {}".format(resp.text)
                message += "\nResponse headers: {}".format(resp.headers)
                message += "\nResponse status code: {}".format(resp.status_code)
                message += "\n{}".format(self.END_REQ)
                log.debug(message)
            except Exception as ex:
                message += "\nResponse URL: {}".format(resp.url)
                message += "\nResponse text: {}".format(resp.text)
                message += "\nResponse headers: {}".format(resp.headers)
                message += "\nResponse status code: {}".format(resp.status_code)
                message += "\n{}".format(self.END_REQ)
                log.error(message)
                raise ApiError(message)
            client.close()
        else:
            raise ApiError("HTTP method is not implemented: {}\n".format(method))
        return resp


class ApiJsonRequest(ApiBase):

    def __init__(self, protocol, host, port):
        super(ApiJsonRequest, self).__init__(protocol, host, port)
        log = Logger(__name__)
        headers = {"Content-Type": "application/json",
                   "Accept": "application/json"}
        self.append_headers(headers)

    def make_request(self, method, uri, payload={}, query_params={}, headers={},
                     is_return_resp_obj=False, raise_error_if_failed=None):
        """
        Args:
            method (str): one of ("get", "post", "put", "delete")
            uri (str): e.g. /v1/someApiRequest
            payload (dict): payload
            query_params (dict): these params will be used in URL
            headers (dict): headers to add to the default ones
            raise_error_if_failed (bool): If a test should fail when response validation failed;
                                          TODO: needs to be implemented
            is_return_resp_obj (bool): True - returns the Response object, False - returns JSON;
                                       Note: it's needed for API testing

        Returns:
            json, (list/dict)
        """
        response_obj = super().make_request(method, uri, payload, query_params, headers)
        if is_return_resp_obj:
            return response_obj
        resp_text = response_obj.text
        response_json = json.loads(response_text)
        # Response validation can be added here.
        # Use raise_error_if_failed and raise AssertionError if validation failed and raise_error_if_failed is True
        return response_json
