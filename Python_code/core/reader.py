import logging
import time
from threading import Thread, Event
from serial.serialutil import SerialException

from Python_code.core.config import setup_logger



setup_logger()


class Reader:
    def __init__(self, connector, disconnect_event):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.connector = connector
        self.disconnect_event = disconnect_event
        self.line = None
        self.key = None
        self.val = None
        self.key_received = Event()
        thread = Thread(target=self.receive, daemon=True)
        thread.start() # поток читающий входящие данные

    def receive(self):
        while True:
            if not self.disconnect_event.is_set():
                try:
                    self.raw_to_line()
                except SerialException:
                    self.logger.warning('При чтении порта ошибка, похоже потеря связи')
                    self.disconnect_event.set()
            time.sleep(0.001)

    def raw_to_line(self):
        raw = self.connector.serial.readline()
        new_line = raw.decode().strip()
        if self.line != new_line:
            self.line = new_line
            self.get_key_val()

    def get_key_val(self):
        if self.line:
            self.key = self.line[0]
            if len(self.line) > 1:
                self.val = max(0.0, min(1.0, float(self.line[1:])))
            else:
                self.val = None
        self.key_received.set()  # Сигналим, что новый ключ пришёл

    def wait_for_key(self, timeout=None):
        """Ждёт следующий ключ (новое нажатие)"""
        self.key_received.clear()  # Сбрасываем событие
        if self.key_received.wait(timeout):  # Ждём новое нажатие
            return self.key, self.val
        return None, None  # Таймаут