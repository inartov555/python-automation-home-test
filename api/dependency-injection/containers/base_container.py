from datetime import timedelta
import json

from dependency_injector import containers

from tools.logger.logger import Logger
from mind_api.url_resolver import UrlResolver
from mind_api.open_api.api_versions import OpenAPIVersion
from shared_components.shared_constants import DateTimeFormats
from tools.utils import DateTimeUtils


class BaseIocContainer(containers.DeclarativeContainer):
    __log = Logger(__name__)

    # list of function_name param for Trio request
    TRIO_REQUEST = ["middle_mind", "auth_conf_search", "fe_body_info_npvr"]

    TRIO_DT_FORMAT = DateTimeFormats.TRIO_DT
    TRIO_REGEX_DT_FORMAT = "[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}"
    OPENAPI_DT_FORMAT = DateTimeFormats.ISO_DATE_TIME_WITH_Z
    OPENAPI_REGEX_DT_FORMAT = "[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z"

    ERR_LOG_RESPONSE_WITH_EMPTY_CONTENT = "Service returned response with empty content"

    @classmethod
    def get_list(cls, settings, url, port, payload, **kwargs):
        """
        JSON param values are set to appropriate fields of a class entity instance.
        This logic should be implemented in the derived containers, if request returns list of items and
        response cannot be constructed in dictionary format because each item has the same keys.
        E.g. list of Channel entities in ServiceOpenAPI#get_channel_search().

        Args:
            settings (Settings): Settings object
            url (str): URL
            port (str): port
            payload (dict): request payload
            **kwargs

        Returns:
            list
        """
        raise NotImplementedError

    @classmethod
    def get_dict(cls, settings, url, port, payload, **kwargs):
        """
        JSON param values are set to appropriate fields of a class entity instance.
        This logic should be implemented in the derived containers, response is constructed in dictionary format
        and keys are different. Also, it may come in handy when you need to group items e.g. programs for a channel
        with ability to define which programs on which channels are airing.

        Notes:
            This method should NOT return raw JSON, the method can be used to return data placed to the entities
            if needed more specific distinguishing e.g. set of grid rows in ServiceOpenAPI#get_guide_rows().

        Args:
            settings (Settings): Settings object
            url (str): URL
            port (str): port
            payload (dict): request payload
            **kwargs

        Returns:
            dict, NOT the raw JSON, some entities contained in the dictionary
        """
        raise NotImplementedError

    @classmethod
    def get_item(cls, settings, url, port, payload, **kwargs):
        """
        JSON param values are set to appropriate fields of a class entity instance.
        This logic should be implemented in the derived containers, if request returns one item.
        E.g. WanIpAddress, it has only one item with IP address.

        Args:
            settings (Settings): Settings object
            url (str): URL
            port (str): port
            payload (dict): request payload
            **kwargs

        Returns:
            BaseEntity, entity item which is derived from BaseEntity
        """
        raise NotImplementedError

    @classmethod
    def _is_openapi_req(cls, function_name):
        """
        !!! FOR USAGE IN CLASSES DERIVED FROM BaseIocContainer ONLY !!!
        It's a switch condition for separating Trio and OpenAPI requests to handle getting and analyzing responses
        when adding OpenAPI equivalent for existing Trio request

        Args:
            function_name (str): MindAPI function's name e.g. middle_mind

        Returns:
            bool, True - OpenAPI request, False - Trio request
        """
        return not cls._is_trio_req(function_name)

    @classmethod
    def _is_trio_req(cls, function_name):
        """
        !!!  FOR USAGE IN CLASSES DERIVED FROM BaseIocContainer ONLY !!!
        It's a switch condition for separating Trio and OpenAPI requests to handle getting and analyzing responses
        when adding OpenAPI equivalent for existing Trio request

        Args:
            function_name (str): MindAPI function's name e.g. middle_mind

        Returns:
            bool, True - Trio request, False - OpenAPI request
        """
        return function_name in cls.TRIO_REQUEST

    @classmethod
    def get_api_version(cls, settings, function_name):
        """
        This method returns the correct version of an OpenAPI request by passed 1st version of the function_name param
        according to the JSON configuration file - mind_api.open_api.open_api_versions.json

        Notes:
            Do not use this method to get the actual request version outside of the BaseIocContainer.
            You can use it outside this class only for comparison e.g. URL params depend on the request version.
            But do not pass this function_name to the make_request() method.

        Args:
            settings (Settings): the settings class, it may have a bit different name, not exactly Settings
            function_name (str): the 1st version of a function name for the OpenAPI request mentioned in
                                 mind_api.middle_mind.mind_api.MindAPI.url_list, e.g. open_api_device_feature_search

        Returns:
            str
        """
        api_version_selector = OpenAPIVersion(settings)
        return api_version_selector.get(function_name)

    @classmethod
    def make_request(cls, settings, url, port, payload, **kwargs):
        """
        Args:
            settings (Settings): Settings object
            url (str): URL
            port (str): port
            payload (dict): request payload
            **kwargs:
                info related to kwargs used by mind_api.url_resolver.UrlResolver.make_request()
                    can be found in description of that method

        Returns:
            response.text, in json format for most of the cases
        """
        if cls._is_openapi_req(kwargs.get("function_name")):
            # Let's set the correct version of an OpenAPI request
            kwargs["function_name"] = cls.get_api_version(settings, kwargs.get("function_name"))
        response = UrlResolver(settings).make_request(url, port, payload, **kwargs)
        if not response:
            cls.__log.warning(cls.ERR_LOG_RESPONSE_WITH_EMPTY_CONTENT)
        return response

    @classmethod
    def convert_openapi_date_format_to_trio_one(cls, openapi_str_dt):
        """
        Converting OpenAPI datetime format to Trio one

        Args:
            openapi_str_dt (str): e.g DateTimeFormatsISO_DATE_TIME_WITH_Z (datetime looks like 2022-07-19T18:55:57Z)

        Returns:
            str, converted date
        """
        return cls.convert_date(openapi_str_dt, cls.OPENAPI_DT_FORMAT, cls.TRIO_DT_FORMAT)

    @classmethod
    def convert_date(cls, str_date, passed_date_format, convert_to_format):
        """
        Converting date from one format to another

        Args:
            str_date (str): e.g. 2022-07-19T18:55:57Z
            passed_date_format (str): e.g. DateTimeFormats.ISO_DATE_TIME_WITH_Z
            convert_to_format (str): e.g. DateTimeFormats.TRIO_DT

        Returns:
            str, converted date
        """
        return DateTimeUtils.convert_date(str_date, passed_date_format, convert_to_format)

    @classmethod
    def dict_update(cls, item_to_be_updated, new_item):
        """
        Smart dict update. Best applicable when dict has embedded dict structures.

        Notes:
            If key is present in both item and value is not of type dict,
                then value of the item_to_be_updated key will be updated with the value of the 2nd one
            If key is present only in new_item, then it'll be added to item_to_be_updated item
            If key is present only in item_to_be_updated, then this param will be left intact

        Args:
            item_to_be_updated (dict): the dict item to merge another dict item to
            new_item (dict): dict item to merge to item_to_be_updated dict

        Returns:
            dict, updated dictionary from item_to_be_updated param
        """
        result = {}
        for key in item_to_be_updated.keys():
            if key in new_item.keys():
                if type(item_to_be_updated[key]) is dict and type(new_item[key]) is dict:
                    result[key] = cls.dict_update(item_to_be_updated[key], new_item[key])
                else:
                    result[key] = new_item[key]
            else:
                result[key] = item_to_be_updated[key]
        for key in new_item.keys():
            if key not in item_to_be_updated.keys():
                result[key] = new_item[key]
        return result

    @classmethod
    def get_timestamp_multiple_of(cls, time_stamp, multiple_of=1800, is_round_to_higher=False):
        """
        Geting time multiple of some value.

        Args:
            time_stamp (int): time in timestamp format e.g. datetime.now().timestamp()
            multiple_of (int): value in seconds the time should be multiple of, one of (900, 1800)
            is_round_to_higher (bool): True - rounding to next half-hour value, applicable to windowStartTime
                                       False - rounding to previous half-hour value, applicable to windowEndTime;
                                       e.g. cur time 14:12:00, so rounding to the next would be 14:30:00
                                       and rounding to the previous would be 14:00:00

        Returns:
            int, time in timestamp format (updated value)
        """
        rounded_time_stamp = time_stamp % multiple_of
        time_stamp_mult_of = time_stamp - rounded_time_stamp
        time_stamp = time_stamp_mult_of if not is_round_to_higher else time_stamp_mult_of + multiple_of
        return int(timedelta(seconds=int(time_stamp)).total_seconds())

    @classmethod
    def get_loop_count(cls, total, devided_by):
        """
        Geting loop count.
        It's applicable when you need to run some number of objects in several rounds e.g. /guideRows
        allows 10 stations (devided_by) for one request max. So if you have, let's say, 100 stations (total),
        and you need to get data for all of them, you'll need this method to run all these stations in several rounds.

        Args:
            total (int): time in timestamp format e.g. datetime.now().timestamp()
            devided_by (int): integer to get number of loop iterations

        Returns:
            int, number of loop iterations
        """
        return int(total // devided_by if total / devided_by == total // devided_by else total // devided_by + 1)

    @classmethod
    def strip_each_item_in_a_list(cls, list_item):
        """
        Removing excess space in the beginnging and in the end on each list item's value
        """
        list_tmp = list()
        for item in list_item:
            if isinstance(item, str):
                list_tmp.append(item.strip())
            else:
                list_tmp.append(item)
        return list_tmp
