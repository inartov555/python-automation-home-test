"""
    @author iurii.nartov@xperi.com
    @created May-26-2022
"""

import json
import os
import re
from http import HTTPStatus
from urllib.parse import urlparse

from tools.logger.logger import Logger
from mind_api.middle_mind.mind_api import MindAPI
from mind_api.sls.sls_api import SlsApi
from shared_components.shared_constants import SharedUrls, MindEnvList
from shared_components.caching import Cacher
from shared_components.singleton import Singleton


class UrlResolver(SlsApi):
    _HTTP = "http"
    CONT_TYPE_TEXT = "text/plain"
    CONT_TYPE_HTML = "text/html"
    CONT_TYPE_JSON = "application/json"
    CONT_TYPE_JSON_UTF_AND_OTHER = "application/json:utf and other"
    HTTP_METHOD_DEFAULT = "post"
    HTTP_PROTOCOL_DEFAULT = _HTTP
    HTTP_STATUS_CODES_OK = [HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.NO_CONTENT]

    def __init__(self, settings):
        self.__log = Logger(__name__)
        self.settings = settings

    def get_base_url_and_port(self, url_string, is_port_pointed):
        """
        Expected URL may look like this: www.xperi.com:443

        Args:
            url_string (str): Either parsed.netloc or parsed.path (if parsed.netloc param is not set),
                              basically it should be URL
            is_port_pointed (bool): Use condition e.g. port_regex.search(parsed.netloc) is None

        Returns:
            tuple, (b_url, p_port)
        """
        b_url = ""
        p_port = ""
        url_string_u = url_string.replace("https://", "").replace(f"{self._HTTP}://", "")
        if is_port_pointed:
            b_url, p_port = re.compile(r"(^(.*):(\d+).*$)").search(url_string_u).groups()[1:]
        else:
            b_url = url_string_u[0:url_string_u.find("/")] if url_string_u.find("/") > 0 else url_string_u
            p_port = ""
        return (b_url, p_port)

    def get_http_prot_url_port_separately(self, url):
        """
        Args:
            url (str): e.g. http://h1.st.tivoservice.com:80

        Returns:
            tuple, (http_protocol, base_url, port, path_uri, query_params)
        """
        port_regex = re.compile(r"(^.*:(\d+).*$)")
        parsed = urlparse(url)
        # When HTTP protocol is not provided, URL is placed to urlparse.path param
        if not parsed.scheme and port_regex.search(parsed.path) is None:
            raise ValueError(f"URL should contain at least HTTP protcol (http/https); current value: {url}")
        base_url, port = self.get_base_url_and_port(
            parsed.netloc or parsed.path,
            port_regex.search(parsed.netloc) is not None or port_regex.search(parsed.path) is not None)
        if parsed.scheme:
            http_protocol = parsed.scheme
        else:
            http_protocol = "https" if port in ("443", "8443") else "http"
        query_params = parsed.query
        if parsed.netloc:
            path_uri = parsed.path
        else:
            path_uri = parsed.path[parsed.path.find("/"):len(parsed.path)] if parsed.path.find("/") > 0 else ""
        if not port:
            port = "443" if http_protocol == "https" else "80"
        return (http_protocol, base_url, port, path_uri, query_params)

    def get_SLS_url(self):
        if "latam" in self.settings.test_environment.lower():
            return SharedUrls.LATAM_SLS
        elif "usqe1" in self.settings.test_environment.lower():
            return SharedUrls.USQE_1_SLS
        return SharedUrls.PROD_SLS

    def make_request(self, url, port, payload, **kwargs):
        """
        Args:
            url (str): URL
            port (str): port
            payload (dict): request payload

        **kwargs:
            mind_version (str): can be middle mind number (if old API is used) or some other value
                                (if new API is used)
            http_protocol (str): one of (http, https)
            http_method (str): one of (post, get, put, delete)
            tsn (str): TiVo serial number
            use_specified_mind_version (bool): True use passed mind version, False - use default mind version, if it's set
            headers (dict): request headers
            update_headers (bool): True - append headers from headers input param to already prepared here,
                                          if param provided;
                                   False - replace headers from headers input param as is, if param provided
            success_status (int): status of successful request e.g. 200, 203, 204
            function_name (str): function name to call from MindApi
            path (str): xpath for dict
            return_status_code (bool): True - returns response status code e.g. 200,
                                       False - returns response content,
                                       None - returns Response object
            part_uri (str): e.g. /device/deleteByDeviceId?deviceId=ca_device_id
            use_query_params (bool): True - adding request type and bodyId params to URL,
                                     False - type and bodyId are not added to URL
            url_params (dict): if set, passed params will be added to URL (URL params)
            error_if_status_not_matched (bool): True - raise ServiceResponseError when response.status_code != status_code,
                                                False - nothing to do

        Returns:
            json, list or dict depending on request
        """
        # Setting of the kwarg params
        mind_version = kwargs.get("mind_version", None)
        http_protocol = kwargs.get("http_protocol", "http")
        http_method = kwargs.get("http_method", self.HTTP_METHOD_DEFAULT).lower()
        tsn = kwargs.get("tsn", self.settings.tsn)
        use_specified_mind_version = kwargs.get("use_specified_mind_version", False)
        headers = kwargs.get("headers", {})
        update_headers = kwargs.get("update_headers", True)
        success_status = kwargs.get("success_status", 200)
        function_name = kwargs.get("function_name", "middle_mind")
        path = kwargs.get("path", None)
        return_status_code = kwargs.get("return_status_code", None)
        part_uri = kwargs.get("part_uri", "")
        use_query_params = kwargs.get("use_query_params", True)  # to add request type and bodyId to URL
        url_params = kwargs.get("url_params", None)  # dict that will be passed as URL params
        # Fail request if status does not match success one or request failed
        error_if_status_not_matched = kwargs.get("error_if_status_not_matched", True)
        mind_version = str(mind_version) if mind_version is not None else None
        if http_method == "get" and url_params and not payload:
            # MindAPI uses payload to fill in params for GET request
            payload = url_params
        # Preparting MindAPI object
        api = MindAPI(
            host=url, port=port, protocol=http_protocol, request_type=http_method, mind_version=mind_version, tsn=tsn,
            use_specified_mind_version=use_specified_mind_version, headers=headers if not update_headers else {})
        make_req_function = eval("api.{function_name}".format(function_name=function_name))
        # Preparting needed function
        api.make_req_function = make_req_function
        # Making a request
        response = api.make_req_function(
            obj=api, status_code=success_status, payload=payload, headers=headers if update_headers else {}, path=path,
            return_status_code=return_status_code, q_params=use_query_params, part_uri=part_uri, query_parms=url_params,
            error_if_status_not_matched=error_if_status_not_matched)
        # Switching all response header keys to lower case
        resp_headers = {key.lower(): value for key, value in response.headers.items()}
        # Validating response
        if response.status_code == HTTPStatus.NO_CONTENT or \
           resp_headers.get("content-type") is None and response.status_code in self.HTTP_STATUS_CODES_OK:
            return None  # should be response with no content
        elif resp_headers.get("content-type") is None and response.status_code not in self.HTTP_STATUS_CODES_OK:
            # None content type
            if error_if_status_not_matched:
                self.increment_error_counter(function_name)
                raise AssertionError(f"Request failed with: {response.text}; status code: {response.status_code}")
            # Sometimes, request may return no value with e.g. 400 status code and you don't need to fail the request
            return None
        elif self.CONT_TYPE_TEXT in resp_headers["content-type"]:
            # TEXT content type
            if not response.text and response.status_code == HTTPStatus.OK and error_if_status_not_matched:
                if "content-length" in resp_headers and resp_headers["content-length"] == "0":
                    return response.status_code
                self.increment_error_counter(function_name)
                raise AssertionError("Reqeust failed. No response text")
            return response.text
        elif self.CONT_TYPE_HTML in resp_headers["content-type"] and error_if_status_not_matched:
            # HTML content type
            self.increment_error_counter(function_name)
            raise AssertionError(f"Request failed with: \n{response.text}")
        elif self.CONT_TYPE_JSON in resp_headers["content-type"]:
            # JSON content type
            if "content-length" in resp_headers and resp_headers["content-length"] == "0":
                # Preserving old behavior
                return response.status_code
            response_json = json.loads(response.text)
            if error_if_status_not_matched and isinstance(response_json, dict):
                type_param = response_json.get("type", "")
                error_keys = ("code", "message", "error")
                if "error" in type_param or any(key in response_json for key in error_keys) or \
                   response.status_code not in self.HTTP_STATUS_CODES_OK:
                    self.increment_error_counter(function_name)
                    raise AssertionError(f"Request failed with: \n{response_json}")
            return response_json
        self.increment_error_counter(function_name)
        raise AssertionError(f"Unhandled Content-Type - '{resp_headers['content-type']}'")

    def increment_error_counter(self, function_name):
        if hasattr(self.settings, 'service_error_counter'):
            if function_name not in self.settings.service_error_counter.keys():
                self.settings.service_error_counter[f"{function_name}"] = 1
            else:
                self.settings.service_error_counter[f"{function_name}"] += 1
            self.__log.error(f"Service API Failure Count: {self.settings.service_error_counter}")

    def __get_group_name(self, env, mso):
        PROD = f"DC_us_mso_{mso}_1"
        STAGING = "DC_Staging"
        USQE1 = "DC_usqe1"
        group_map = {"prod-armstrong": PROD,
                     "prod-astound": PROD,
                     "prod-blueridge": PROD,
                     "prod-bluestream": PROD,
                     "prod-breezeline": PROD,
                     "prod-eastlink": PROD,
                     "prod-entouch": PROD,
                     "prod-hotwire": PROD,
                     "prod-llacr": PROD,
                     "prod-llacar": PROD,
                     "prod-llapa": PROD,
                     "prod-metronet": PROD,
                     "prod-midco": PROD,
                     "staging-millicom": "DC_us_retail_5",
                     "prod-rcn": PROD,
                     "prod-secv": PROD,
                     "prod-tds": PROD,
                     "prod-telus": PROD,
                     "usqe3a-cableco": "DC_us_mso_CableCo_1",
                     "latam_prod-millicom": "DC_latam_mso_mic_1",
                     "latam_prod-llacl": "DC_latam_mso_llacl_1",
                     "latam_prod-vtr": "DC_latam_mso_llacl_1",
                     "latam_prod-claro": "DC_latam_mso_llacl_1",
                     "latam_staging-cableco12": "DC_latam_st",
                     "staging-astound": STAGING,
                     "staging-cableco": STAGING,
                     "staging-cableco11": STAGING,
                     "staging-cableco3": STAGING,
                     "staging-cableco5": STAGING,
                     "staging-tds": STAGING,
                     "usqe1-cableco11": USQE1,
                     "usqe1-cableco3": USQE1,
                     "usqe1-cableco5": USQE1,
                     }
        group = group_map.get(f"{env}-{mso}", "DC_us_retail_5")
        return group

    @Cacher.process
    def _get_all_endpoints_str(self, use_cached_response=True):
        """
        Getting endpoints response as is in str.

        Example of returned value:
            bridge-keeper:production.bridge-keeper.prod.tivoservice.com:443
            casting-drm-device:api-casting-drm-device-lambda-usqe1.dev.tivoservice.com:443
            cc-vod-ott-action-details:api-cc-vod-ott-action-details-usqe1.dev.tivoservice.com:443
            channel-logo-image-host:i.tivo.com:80

        Args:
            use_cached_response (bool): True - using cached response
                                        (request will be made only if there's no cached value,
                                        may make test running faster),
                                        False - making request each time when this method is called

        Returns:
            str
        """
        headers = {"Content-Type": self.CONT_TYPE_TEXT, "Accept": self.CONT_TYPE_TEXT}
        SLS_url = self.get_SLS_url()
        http_protocol, url_base, port = self.get_http_prot_url_port_separately(SLS_url)[0:3]
        if self.settings.tsn:
            payload = {"bodyId": "tsn:" + self.settings.tsn}
            endpoint = "/Search"
        else:
            payload = {"group": self.__get_group_name(self.settings.test_environment, self.settings.mso)}
            endpoint = "/GroupConfig"
        resp_text = self.make_request(
            url_base, port, payload, http_protocol=http_protocol, http_method="get",
            function_name="endpoint_for_service", part_uri=endpoint, use_query_params=True, headers=headers,
            update_headers=False)
        return resp_text

    def get_endpoints(self, endpoint_key=None, use_cached_response=True):
        """
        /Search?bodyId=tsn:{tsn}
        Works also for production.

        Example of returned value:
            {'aps': 'https://api-aps.staging.tivoservice.com:443',
            'bridge-keeper': 'https://production.bridge-keeper.prod.tivoservice.com:443',
            'channel-service': 'https://aps-channels-lambda-staging.prod.tivoservice.com:443',
            'channels-iptv': 'https://api-channels-service-lambda-staging.prod.tivoservice.com:443'}

        Args:
            endpoint_key (str): key to get particular URL from available list e.g. ("aps", "bridge-keeper", "channel-service")
            use_cached_response (bool): True - getting cached value, False - making request

        Returns:
            dict, map of {endpoint key: URL} if endpoint_key is NOT set
            str, if endpoint_key is set (definite URL)
        """
        resp_text = self._get_all_endpoints_str(use_cached_response)
        # Turning text response into dict
        if isinstance(resp_text, str):
            tmp_list = resp_text.strip().split("\n")  # response may be with empty line in the end
        else:
            raise AssertionError(f"get_endpoints: no endpoints returned - '{resp_text}'\n\n"
                                 "Possible reasons:\n"
                                 "   1. Box is not bound to account\n"
                                 "   2. Box is bound to an account with different MSO\n"
                                 "      (e.g. you run tests on CC11 but box bound to CC3)\n")
        param_url_dict = self.get_service_global_endpoints(self.settings.tsn)  # merging the global SLS URLs
        for item in tmp_list:
            frst_colon_indx = item.find(":")
            key = item[:frst_colon_indx]
            value = item[frst_colon_indx + 1:]
            protocol = self._HTTP + "s" if ":443" in value or ":8443" in value else self._HTTP
            full_url = f"{protocol}://{value}"
            if key:
                # Skipping empty params
                param_url_dict[key] = full_url
            # sharing containers using OS env for analytics
            env_name = value.replace('.', '').replace(':', '').replace('-', '').upper()
            os.environ[env_name] = key
        if endpoint_key and endpoint_key in param_url_dict:
            return param_url_dict[endpoint_key]
        elif endpoint_key and endpoint_key not in param_url_dict:
            raise AssertionError(f"get_endpoints: {endpoint_key} not found in {param_url_dict}\n\n"
                                 "Possible reasons:\n"
                                 "   1. Check if TSN is correct\n"
                                 "   2. Incorrect endpoint key was passed\n"
                                 "   3. Device binding was removed for device (tveServiceReset was called)\n"
                                 f"   4. Perhaps, {endpoint_key} service has not been deployed yet\n"
                                 "   5. Check if an actually used by a box CA Device ID was passed to UTAF\n")
        return param_url_dict
