import logging
import time


from threading import Thread

from Python_code.managers.app_manager import AppManager
from Python_code.managers.device_manager import DeviceManager
from Python_code.core.reader import Reader
from Python_code.core.connector import Connector
from Python_code.core.tray_icon import TrayIcon
from Python_code.core.message import Message
from Python_code.core.config import setup_logger

from Python_code.Handlers.default_handler import Default
from Python_code.Handlers.OBS_handler import OBS
from Python_code.Handlers.containers import Services, Events


setup_logger()


class Handler:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.tray = TrayIcon()
        self.msg = Message()
        self.connector = Connector(self.msg, self.tray.shutdown_event)
        self.disconnect_event = self.connector.disconnect_event
        self.app_manager = AppManager(self.disconnect_event, self.msg)
        self.device_manager = DeviceManager(self.disconnect_event)
        self.audio_disconnect_event = self.device_manager.audio_disconnect_event
        self.mic_disconnect_event = self.device_manager.mic_disconnect_event
        self.reader = Reader(self.connector, self.disconnect_event)

        self.services = Services(
            connector=self.connector,
            reader=self.reader,
            app_manager=self.app_manager,
            device_manager=self.device_manager,
            msg=self.msg
        )

        self.events = Events(
            audio_disconnect_event=self.device_manager.audio_disconnect_event,
            mic_disconnect_event=self.device_manager.mic_disconnect_event,
            disconnect_event=self.disconnect_event
        )

        self.default = Default(self.services, self.events)
        self.obs = OBS(self.services, self.events)

        self.keys = {
            'A': None,
            'B': None,
            'C': None,
            'D': None,
            'M': None,
            'V': None,
            'K': None,
            'P': None,
            'S': None,
            'N': None
        }
        self.path = 'binds.json'
        self.load_binds()

        thread = Thread(target=self.process, daemon=True)
        thread.start() # поток обработки входящих данных

    def process(self):
        while True:
            if not self.disconnect_event.is_set():
                key, val = self.reader.wait_for_key(3)
                if key or val:
                    try:
                        self.keys[key](key, val)
                        self.reader.line = None
                        self.reader.key = None
                        self.reader.val = None
                    except:
                        self.logger.debug(f'На кнопку {key} не назначена команда')
                    time.sleep(0.001)
            else:
                time.sleep(3)

    def load_binds(self):
        pass