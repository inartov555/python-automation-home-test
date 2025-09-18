import json

from dependency_injector import containers

from tools.logger import Logger


class BaseIocContainer(containers.DeclarativeContainer):
    __log = Logger(__name__)

    @classmethod
    def get_list(cls, settings, url, port, payload, **kwargs):
        """
        JSON param values are set to appropriate fields of a class entity instance.
        This logic should be implemented in the derived containers, if request returns list of items and
        response cannot be constructed in dictionary format because each item has the same keys.

        Args:
            settings (Settings): Settings object
            url (str): URL
            port (str): port
            payload (dict): request payload

        Returns:
            list
        """
        raise NotImplementedError

    @classmethod
    def get_dict(cls, settings, url, port, payload, **kwargs):
        """
        JSON param values are set to appropriate fields of a class entity instance.
        This logic should be implemented in the derived containers, response is constructed in dictionary format
        and keys are different.

        Notes:
            This method should NOT return raw JSON, the method can be used to return data placed to the entities

        Args:
            settings (Settings): Settings object
            url (str): URL
            port (str): port
            payload (dict): request payload

        Returns:
            dict, NOT the raw JSON, some entities contained in the dictionary
        """
        raise NotImplementedError

    @classmethod
    def get_item(cls, settings, url, port, payload, **kwargs):
        """
        JSON param values are set to appropriate fields of a class entity instance.
        This logic should be implemented in the derived containers, if request returns one item.

        Args:
            settings (Settings): Settings object
            url (str): URL
            port (str): port
            payload (dict): request payload

        Returns:
            BaseEntity, entity item which is derived from BaseEntity
        """
        raise NotImplementedError

    @classmethod
    def make_request(cls, settings, url, port, payload, **kwargs):
        """
        Args:
            settings (Settings): Settings object
            url (str): URL
            port (str): port
            payload (dict): request payload

        Returns:
            json, response in json format
        """
        if cls._is_openapi_req(kwargs.get("function_name")):
            # Let's set the correct version of an OpenAPI request
            kwargs["function_name"] = cls.get_api_version(settings, kwargs.get("function_name"))
        response = UrlResolver(settings).make_request(url, port, payload, **kwargs)
        return response
