from abc import ABCMeta, abstractmethod

from tools.logger.logger import Logger


class BaseEntity(metaclass=ABCMeta):
    __log = Logger(__name__)

    @abstractmethod
    def __init__(self, dict_item):
        """
        Args:
            dict_item (dict): dict item of the JSON response
        """
        self.__not_set_with_value_debug = {}  # contains a map with params and bool value for having/not having value
        self.__dict_item = {} if not dict_item else dict_item
        if not self.__dict_item:
            self.__log.warning("{}: Got a dict item with no any params".format(type(self).__name__))
        elif type(self.__dict_item) is not dict:
            self.__log.error("{}: Constructor input param should be dict, current type - {}, value - {}"
                             .format(type(self).__name__, type(self.__dict_item).__name__, self.__dict_item))

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict_item})"

    @property
    def dict_item(self):
        """
        Get whole dict the class was initiated with

        Returns:
            dict
        """
        return self.__dict_item

    def print_not_set_and_params_with_value(self):
        """
        Printing debug info to log
        """
        self.__log.debug("Params with bool flag to show set/not not set value: {}".format(self.__not_set_with_value_debug))

    def _value(self, json_object, *nodes):
        """
        Get value of the JSON object for passed key. If there are params that have dict as a value

        Args:
            *nodes (list): value of last list item will be returned
                           Note that all parent params need to be listed before
                           the embedded param the value is being got of
            json_object (dict): the dict object to iterate

        Returns:
            value for passed key of JSON object
        """
        json_object_u = json_object if json_object else {}
        if type(json_object_u) is not dict:
            raise ValueError("json_object must be dict")
        if json_object_u:
            for node in nodes:
                if node not in json_object_u:
                    # self.__log.error("_value: Item doesn't contain key: '{}', Item: '{}' \n".format(node, json_object_u))
                    self._append_not_set_and_params_with_value(False, *nodes)
                    return None
                if type(json_object_u) is not dict:
                    raise ValueError(f"Cannot proceed with extracting value of {node} item since object to compare "
                                     f"is not dict; obj type: {type(json_object_u)}; object: {json_object_u}")
                json_object_u = json_object_u[node]
                # Setting bool value in Python format
                if str(json_object).lower() == "true":
                    json_object = True
                elif str(json_object).lower() == "false":
                    json_object = False
            self._append_not_set_and_params_with_value(True, *nodes)
            return json_object_u
        # Most likely, there's no json param or it does not have value
        self._append_not_set_and_params_with_value(False, *nodes)
        return None

    def _append_not_set_and_params_with_value(self, is_set, *nodes):
        """
        This method allocates not set and params with values to an appropriate dict.

        Args:
            is_set (bool): True - param has some value, False - param is not set
            *nodes (tuple): params
        """
        if len(nodes) == 1:
            self.__not_set_with_value_debug[nodes[0]] = is_set
        if len(nodes) > 1:
            params = ""
            for node in nodes:
                params += str(node) + "->"
            self.__not_set_with_value_debug[params] = is_set
