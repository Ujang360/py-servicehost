import sys

from typing import List, Callable
from logging import Logger
from signal import SIGINT, SIGTERM, Signals, pause, signal


class ServiceHost(object):
    _instance = None
    _logger: Logger
    _start_methods: List[Callable[[None], None]]
    _stop_methods: List[Callable[[None], None]]

    def __init__(self, logger: Logger, force_instantiate: bool = False):
        if ServiceHost._instance is not None and force_instantiate is False:
            return
        self._logger = logger
        self._start_methods = []
        self._stop_methods = []
        ServiceHost._instance = self

    @staticmethod
    def get_instance(force_instantiate: bool = False):
        if ServiceHost._instance is None or force_instantiate is True:
            ServiceHost()
        return ServiceHost._instance

    @staticmethod
    def register_service(
        service_start_method: Callable[[None], None],
        service_stop_method: Callable[[None], None],
    ):
        instance = ServiceHost.get_instance()
        if isinstance(service_start_method, Callable[[None], None]) is not True:
            raise TypeError("service start method must be Callable[[None], None]")
        if isinstance(service_stop_method, Callable[[None], None]) is not True:
            raise TypeError("service stop method must be Callable[[None], None]")
        instance._start_methods.append(service_start_method)
        instance._stop_methods.append(service_stop_method)

    def _start_services(self):
        self._logger.info("Starting services...")
        for start_method in self._start_methods:
            start_method()
        self._logger.info("Starting services DONE")

    def _stop_services(self):
        self._logger.info("Stopping services...")
        for stop_method in self._stop_methods:
            stop_method()
        self._logger.info("Stopping services DONE")

    def _signal_handler(self, sig, frame):
        self._register_signal(clear=True)
        print()  # aesthetic hack, do not remove
        self._logger.info(f"{Signals(sig).name} caught, stopping sequence initiated...")
        self._stop_services()
        self._logger.info("Exiting...")
        sys.exit(0)

    def _empty_signal_handler(self, sig, frame):
        pass

    def _register_signal(self, clear=False):
        if clear:
            signal(SIGINT, self._empty_signal_handler)
            signal(SIGTERM, self._empty_signal_handler)
        else:
            signal(SIGINT, self._signal_handler)
            signal(SIGTERM, self._signal_handler)

    def run(self):
        self._register_signal()
        self._start_services()
        pause()
