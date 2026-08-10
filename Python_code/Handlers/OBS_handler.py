import time

import obsws_python as obs
import logging
import json
import os
import threading
from threading import Event

from Python_code.core.config import setup_logger



setup_logger()


class OBS:
    def __init__(self, services, events):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.services = services
        self.events = events
        self.msg = services.msg

        self.keys = {
            'A': self.set_channel_volume,
            'B': self.set_channel_volume,
            'C': self.set_channel_volume,
            'D': self.set_channel_volume,
            'M': None,
            'V': None,
            'K': None,
            'P': self.mute_channel_volume,
            'S': self.mute_channel_volume,
            'N': self.mute_channel_volume
        }

        self.path = 'data/obs_settings.json'
        self.channels  ={
            'A': '',
            'B': '',
            'C': '',
            'D': ''
        }
        self.psw = 'psw'
        self.port = 4455
        self.load_fr_file()
        self.client = None

        self.connect_obs_event = Event()
        self.connect_obs_event.clear()
        self.connection_obs_thread = threading.Thread(target=self.connect_loop, daemon=True)
        self.connection_obs_thread.start()

    def connect_loop(self):
        """Основной цикл проверки подключения"""
        while True:
            if not self.connect_obs_event.is_set():
                self.logger.info('Пытаемся подключиться к OBS...')
                self.try_connect_obs()
            time.sleep(3)

    def try_connect_obs(self):
        """Цикл подключения к OBS"""
        while not self.connect_obs_event.is_set():
            try:
                self.client = obs.ReqClient(host='localhost', port=self.port, password=self.psw or '')
                self.logger.info('Подключились к OBS')
                self.msg.notification('OBS', 'Подключились к OBS', 'connected')
                self.connect_obs_event.set()
            except Exception as err:
                self.logger.debug(f'Не удалось подключиться: {err}')
            time.sleep(3)

    def set_channel_volume(self, key, val):
        """Установить громкость канала"""
        channel = self.channels.get(key)
        if not channel:
            self.logger.debug(f'Непривязанный канал: {key}')
            return
        if not self.client or not self.connect_obs_event.is_set():
            self.logger.debug('Нет подключения к OBS')
            return
        try:
            val = max(0.0, min(1.0, val))
            self.client.set_input_volume(channel, val)
            self.logger.debug(f'{channel} громкость: {int(val * 100)}%')
        except:
            self.logger.debug(f'Неправильное название канала {channel}')

    def mute_channel_volume(self, key, val):
        """Переключить mute для канала"""
        if not self.client or not self.connect_obs_event.is_set():
            self.logger.debug('Нет подключения к OBS')
            return
        match key:
            case 'P': name = self.channels.get('B')
            case 'S': name = self.channels.get('C')
            case 'N': name = self.channels.get('D')
            case _: self.logger.warning(f'Неизвестный ключ mute: {key}'); return
        if not name:
            self.logger.debug(f'Канал для {key} не привязан')
            return
        try:
            # Получаем текущее состояние и переключаем
            current = self.client.get_input_mute(name).input_muted
            new_state = not current
            # Устанавливаем новое состояние
            self.client.set_input_mute(name, new_state)
            # Логируем результат
            state_text = 'заглушен' if new_state else 'включён'
            self.logger.debug(f'{name}: {state_text}')
        except Exception as e:
            self.logger.error(f'Ошибка переключения mute для {name}: {e}')
            self.connect_obs_event.clear()

    def load_fr_file(self):
        """Подгружает текущие настройки из файла"""
        if os.path.exists(self.path):
            with open(self.path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.channels = {
                'A': data.get('A'),
                'B': data.get('B'),
                'C': data.get('C'),
                'D': data.get('D')
            }
            self.psw = data.get('password')
            self.port = data.get('port')
            self.logger.info("Загрузили настройки из файла")
        else:
            self.logger.info("Нет файла с настройками OBS")