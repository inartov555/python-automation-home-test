from mind_api.dependency_injection.entities.base_entity import BaseEntity


class AuthConfigurationSearch(BaseEntity):
    def __init__(self, dict_item):
        """
        OpenAPI authConfigurations

        Args:
            dict_item (dict): dict item of the JSON response
        """
        super().__init__(dict_item)
        self.__domain = self._value(self.dict_item, "domain")
        self.__license_plate_url = self._value(self.dict_item, 'licensePlateUrl')
        self.__drm_type = self._value(self.dict_item, 'drmType')
        self.__authentication_type = self._value(self.dict_item, 'authenticationType')
        self.__display_rank = self._value(self.dict_item, 'displayRank')

    @property
    def domain(self):
        """
        Returns:
            str, e.g. cableco11-dbs
        """
        return self.__domain

    @property
    def license_plate_url(self):
        """
        Returns:
            str, e.g. http://devicebindingservice.tpa1.tivo.com:50207
        """
        return self.__license_plate_url

    @property
    def drm_type(self):
        return self.__drm_type

    @property
    def authentication_type(self):
        """
        Returns:
            str, one of (dbsPreBinding, dbsLicensePlateBinding,)
        """
        return self.__authentication_type

    @property
    def display_rank(self):
        """
        Returns:
            int
        """
        return self.__display_rank
