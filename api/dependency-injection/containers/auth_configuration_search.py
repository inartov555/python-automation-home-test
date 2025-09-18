from mind_api.dependency_injection.entities.auth_configuration_search import AuthConfigurationSearch
from tools.logger.logger import Logger
from mind_api.dependency_injection.containers.base_container import BaseIocContainer


class AuthConfigurationSearchIocContainer(BaseIocContainer):
    __log = Logger(__name__)

    @classmethod
    def get_item(cls, settings, url, port, payload, **kwargs):
        """
        JSON param values are set to appropriate fields of a class entity instance.

        Args:
            settings (Settings): Settings object
            url (str): URL
            port (str): port
            payload (dict): request payload

        **kwargs:
            mso_name: str, f.e. cableco5
            info related to kwargs used by mind_api.url_resolver.UrlResolver.make_request()
                can be found in description of that method

        Returns:
            AuthConfigurationSearch
        """
        auth_configuration = {}
        function_name = kwargs.get('function_name', None)
        cls.__log.info("Getting AuthConfigurationSearch item")
        response = cls.make_request(settings, url, port, payload, **kwargs)

        if cls._is_trio_req(function_name):
            auth_configuration.update(response['authenticationConfiguration'][0])

        if cls._is_openapi_req(function_name):
            auth_configuration.update(response['authconfigurations'][0])

        # As response already returned as dict for both OpenApi and Mind versions,
        # no need to check additional fields inside

        return AuthConfigurationSearch(auth_configuration)
