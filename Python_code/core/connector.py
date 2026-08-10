import threading
import serial
import serial.tools.list_ports
import logging
import time

from Python_code.core.config import setup_logger



setup_logger()


class Connector:
    def __init__(self, msg, shutdown_event):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.disconnect_event = threading.Event()  # True = отключен, False = подключен
        self.disconnect_event.set() # изначально отключен
        self.shutdown_event = shutdown_event
        self.msg = msg
        self.serial = None
        self.PIDs = ['PID=2341:8036',
                     'PID=2341:8037']
        self.open_serial()
        self.check_thread = threading.Thread(target=self.check_connect)
        self.check_thread.start() #поток проверяющий подключение

    def check_connect(self):
        while not self.shutdown_event.is_set():
            if self.disconnect_event.is_set():
                self.close_port()
                self.open_serial()
            time.sleep(3)
        self.disconnect_event.set()
        self.close_port()

    def open_serial(self):
        """Основной метод подключения"""
        self.logger.info('Пытаемся установить связь...')
        while self.disconnect_event.is_set():
            self.try_open_serial()
            if self.disconnect_event.is_set():
                time.sleep(3)

    def try_open_serial(self):
        try:
            for port in serial.tools.list_ports.comports():
                if any(pid in port.hwid for pid in self.PIDs):
                    arduino_port = port.device
                    self.serial = serial.Serial(arduino_port, 9600, timeout=1)
                    self.logger.info(f'Установили связь через порт {arduino_port}')
                    self.msg.notification('Устройство подключено', 'Всё готово к работе!', 'connected')
                    self.disconnect_event.clear()  # подключен
                    return
        except Exception as err:
            self.logger.error(err)
            return

    def close_port(self):
        """Безопасное закрытие порта"""
        if self.serial:
            try:
                self.serial.close()
                self.logger.info("Порт закрыт")
                self.msg.notification('Устройство отключено', 'Ждём подключения...', 'disconnected')
            except Exception as e:
                self.logger.error(f"Ошибка при закрытии порта: {e}")
            finally:
                self.serial = None