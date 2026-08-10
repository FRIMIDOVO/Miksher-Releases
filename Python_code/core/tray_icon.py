import logging
import pystray
from PIL import Image
import threading

from Python_code.core.config import setup_logger

setup_logger()


class TrayIcon:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.shutdown_event = threading.Event()
        self.shutdown_event.clear()
        self.menu_set = None
        icon_path = "data/иконка.png"
        try:
            self.image = Image.open(icon_path)
        except Exception as e:
            self.logger.error(f"Не удалось загрузить иконку: {e}")
            self.image = Image.new('RGB', (64, 64), color='white')
        self.menu = pystray.Menu(pystray.MenuItem("Выход", self._exit_program))
        self.icon = pystray.Icon(
            name="Miksher",
            icon=self.image,
            title="Miksher",
            menu=self.menu)
        # Запускаем в отдельном потоке
        self.thread = threading.Thread(target=self.icon.run, daemon=True)
        self.thread.start()
        self.logger.info("Трей успешно загружен")

    def _exit_program(self, icon, item):
        self.logger.info("Завершение программы...")
        self.shutdown_event.set()
        self.icon.stop()