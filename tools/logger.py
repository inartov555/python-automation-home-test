import logging
import logging.config
import os
import sys
import string
import datetime

from tools import analytics

# Create a new log level
logging.STEP = 32
logging.addLevelName(logging.STEP, 'STEP')  # new level


def step(self, message, *args, **kws):
    if self.isEnabledFor(logging.STEP):
        self._log(logging.STEP, message, args, **kws)


logging.Logger.step = step


class Logger:
    """
    Wrapper over logging class that initializes a logger with the config in 'tools/logger/logging.json'
    To modify default log level edit in 'tools/logger/logging.json' the parameter json['handlers']['console']['info']
    Logging path is LOG_PATH if defined else it's project root dir(not recommended)

    @param logger_name: altough any name ca be used it's recommended to use __name__ python variable
    """
    __file_handler = None
    __cli_handler = None
    __loggers = []  # links to all created loggers
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    def __init__(self, logger_name):
        # creating logger
        if not logger_name.startswith("utaf"):
            logger_name = f"utaf.{logger_name}"
        self.__logger = logging.getLogger(logger_name)
        # self.__logger.propagate = True
        if self.__logger not in Logger.__loggers:
            Logger.__loggers.append(self.__logger)

    def step(self, message):
        analytics.SnoozeAnalytics().add_step_event(message)
        self.__logger.step(message)

    def info(self, message):
        self.__logger.info(message)

    def debug(self, message):
        m1 = ''.join(filter(lambda x: x in string.printable, message))
        self.__logger.debug(m1)

    def error(self, message):
        self.__logger.error(message)

    def warning(self, message):
        self.__logger.warning(message)

    def __update_handler(self, logr, handlr):
        """
        Update loggers handler with new log level. The method will get all handlers of logger and change level
        of existing logger if the handler already setup for logger
        Args:
            logr: logger, logger to be updated
            handlr: handler, handler with required level and config

        Returns:
            None
        """
        for hdlr in logr.handlers:
            if hdlr.name == handlr.name:
                hdlr.level = handlr.level
                break
        else:
            logr.addHandler(handlr)

    def __get_file_handler(self, level, filename):
        """
        method to create file handler or get it from a cash
        Args:
            level: str, level name

        Returns:

        """
        if not Logger.__file_handler:
            file_handler = logging.FileHandler(filename)
            formatter = logging.Formatter(self.log_format)
            file_handler.setFormatter(formatter)
            file_handler.setLevel(level)
            file_handler.name = "main_log_file"
            Logger.__file_handler = file_handler
        return Logger.__file_handler

    def __get_cli_handler(self, level):
        """
        method to create Stream handler or get it froma cash
        Args:
            level: str, level name

        Returns:

        """
        if not Logger.__cli_handler:
            formatter = logging.Formatter(self.log_format)
            cli_handler = logging.StreamHandler(sys.stdout)
            cli_handler.setFormatter(formatter)
            cli_handler.setLevel(level)
            cli_handler.name = "console"
            Logger.__cli_handler = cli_handler
        return Logger.__cli_handler

    def setup_cli_handler(self, level):
        """
        Method to set up CLI handler for particular logger or all available
        If CLI handler was set up for all loggers then all new will be created with the same config

        Args:
            level: str or int, level for the file handler

        Returns: None
        """
        cli_handler = self.__get_cli_handler(level)
        root_logger = logging.getLogger()
        self.__update_handler(root_logger, cli_handler)
        root_logger.setLevel(min(cli_handler.level, root_logger.level))

    def setup_filehandler(self, filename, level="DEBUG"):
        """
        Method to setup file handler for particular logger or all available
        If file handler was setup for all loggers then all new will be created with the same config

        Args:
            filename: str, path where logs should be stored
            level: str or int, level for the file handler
            logger_name: str, name of logger file handler to be applied for

        Returns: None
        """
        root_logger = logging.getLogger()
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        loggers_list = []
        loggers_list.append(root_logger)
        file_handler = self.__get_file_handler(level, filename)
        for logger in loggers_list:
            self.__update_handler(logger, file_handler)
        root_logger.setLevel(min(file_handler.level, root_logger.level))


class PerfLogger:

    def __init__(self, shared_space):
        self.shared_space = shared_space
        self.shared_space.vt_result = {}
        self.__logger = Logger("perf_logger")
        self.run_name = ""

    def _dump_to_file(self, data):
        if hasattr(self.shared_space, "log_path") and self.shared_space.log_path:
            filename = os.path.join(self.shared_space.log_path, "client_performance.log")
            with open(filename, "a") as fe:
                for kpi, value in data.items():
                    fe.write(f"{datetime.datetime.now()}::::{self.run_name}: {kpi} = {value}s \n")

    def perf_log(self, kpi, value):
        self.__logger.step("Performance log kpi: {} = {} ".format(kpi, value))
        if not isinstance(value, (int, float)):
            data = {kpi: value}
        else:
            data = {kpi: "{:.4f}".format(value)}
        self.shared_space.vt_result.update(data)
        self._dump_to_file(data)

    def log_data(self, data: dict):
        self.__logger.step("Extend logger got data: {}".format(data))
        self.shared_space.vt_result.update(data)
        self._dump_to_file(data)
