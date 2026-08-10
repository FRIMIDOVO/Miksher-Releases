from winotify import Notification, audio
import logging
import os
import json

from Python_code.core.config import setup_logger



setup_logger()


class Message:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.path = os.path.abspath("data/иконка.ico")
        self.set_path = "data/not_settings.json"
        self.scens = {
            'connected': audio.Reminder,
            'disconnected': audio.Mail,
            'change_audio': audio.SMS,
            'new_bind': audio.SMS,
            'new_realise': audio.Mail
        }
        self.settings = {
            'connected': True,
            'disconnected': True,
            'change_audio': True,
            'new_bind': True,
            'volume': True
        }
        # ещё иконки под каждый сценарий разные можна
        self.load_settings()

    def notification(self, title, text, scen, long_short='short'):
        """Показать уведомление"""
        if not self.settings.get(scen):
            self.logger.debug(f'Уведомления для {scen} выключены')
            return
        try:
            notif = Notification(
                app_id="Miksher",
                title=title,
                msg=text,
                duration=long_short,
                icon=self.path
            )
            if self.settings.get('volume'):
                notif.set_audio(self.scens.get(scen), loop=False)
            notif.show()
            self.logger.info('Отправили уведомление')
        except Exception as e:
            self.logger.error(f"Ошибка уведомления: {e}")

    def load_settings(self):
        """Загружает настройки уведомлений из файла"""
        try:
            with open(self.set_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.settings.update(data)
        except:
            self.logger.error("Похоже файла с настройками нет, настройки по умолчанию")
            return
        self.settings = {
            'connected': data.get('connection_not'),
            'disconnected': data.get('disconnection_not'),
            'change_audio': data.get('change_audio_not'),
            'new_bind': data.get('bind_not'),
            'volume': data.get('sound_not')
        }
        self.logger.info("Загружены настройки из файла")