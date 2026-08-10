import logging

import win32api
import win32gui
from pycaw.pycaw import AudioUtilities
import pyautogui

from Python_code.core.config import setup_logger



setup_logger()


class Default:
    def __init__(self, services, events):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.services = services
        self.events = events

        self.connector = services.connector
        self.reader = services.reader
        self.app_manager = services.app_manager
        self.device_manager = services.device_manager
        self.msg = services.msg

        self.audio_disconnect_event = events.audio_disconnect_event
        self.mic_disconnect_event = events.mic_disconnect_event

        self.keys = {
            'A': self.master_volume,
            'B': self.app_volume,
            'C': self.app_volume,
            'D': self.app_volume,
            'M': self.microphone_state,
            'V': self.volume_state,
            'K': self.bind,
            'P': self.music,
            'S': self.music,
            "N": self.music
        }
        self.is_mic_mute = False
        self.is_volume_mute = False
        self.audio_ind = -1
        self.audio_dev = None
        self.audio_obj = None
        self.mic_ind = 0
        self.mic_dev = None
        self.mic_obj = None

    def music(self, key, val):
        match key:
            case 'P': pyautogui.press('prevtrack')
            case 'S': pyautogui.press('playpause')
            case 'N': pyautogui.press('nexttrack')

    def master_volume(self, key, val):
        """Устанавливает громкость системы"""
        if not self.is_volume_mute and not self.audio_disconnect_event.is_set():
            try:
                self.audio_obj.SetMasterVolumeLevelScalar(val, None)
            except:
                self.logger.error('Похоже устройство отключено, переключаем на ближайшее...')
                self.change_audio()
        else:
            return

    def app_volume(self, key, val):
        """Устанавливает громкость приложения"""
        if self.audio_disconnect_event.is_set():
            return
        if self.audio_obj:
            app = self.app_manager.sessions.get(key)
            app.SetMasterVolume(val, None) if app else None
        else:
            self.logger.error('Похоже устройство отключено, переключаем на ближайшее...')
            self.change_audio()

    def microphone_state(self, key, val):
        """Изменяет состояние микрофона"""
        if self.mic_disconnect_event.is_set():
            return
        if self.mic_obj:
            hwnd = win32gui.GetForegroundWindow()
            win32api.SendMessage(hwnd, 0x0319 , None, 0x180000)
            self.is_mic_mute = not self.mic_obj.GetMute()
            if self.is_mic_mute:
                self.connector.serial.write(b'M1\n')
                self.logger.debug('Микрофон выключен')
            else:
                self.connector.serial.write(b'M0\n')
                self.logger.debug('Микрофон включен')
        else:
            self.logger.error('Похоже устройство отключено, переключаем на ближайшее...')
            self.mic_dev = list(self.device_manager.mic_dict.keys())[self.mic_ind]
            self.mic_obj = self.device_manager.mic_dict[self.mic_dev]

    def volume_state(self, key, val):
        """Изменяет состояние громкости системы"""
        if self.audio_disconnect_event.is_set():
            return
        if self.audio_obj:
            hwnd = win32gui.GetForegroundWindow()
            win32api.SendMessage(hwnd, 0x0319, None, 0x80000)
            self.is_volume_mute = not self.audio_obj.GetMute()
            if self.is_volume_mute:
                self.connector.serial.write(b"V1\n")
                self.logger.debug('Звук выключен')
            else:
                self.connector.serial.write(b"V0\n")
                self.logger.debug('Звук включен')
        else:
            self.logger.error('Похоже устройство отключено, переключаем на ближайшее...')
            self.change_audio()

    def bind(self, key, val):
        """Либо изменяет работающее устройство воспроизведения
            либо биндит опр. key на активное приложение"""
        self.logger.debug('Ждём...')
        next_key = None
        while next_key not in ('B', 'C', 'D', 'K'):
            next_key, next_val = self.reader.wait_for_key(timeout=3)
        self.logger.debug(f'Дождались {next_key, next_val}')
        if next_key == 'K':
            self.change_audio()
            self.logger.debug('K')
        elif next_key in ('B', 'C', 'D'):
            self.app_manager.bind(next_key)
            self.logger.debug('BCD')

    def change_audio(self):
        if len(self.device_manager.audio_dict.keys()) == 1 and self.audio_obj:
            self.logger.info("У вас единственное устройство")
            self.msg.notification('🎧 Не переключено', 'У вас единственное устройство', 'change_audio')
            return
        if self.audio_disconnect_event.is_set():
            return
        devices = list(self.device_manager.audio_dict.keys())
        new_ind = (self.audio_ind + 1) % len(devices)
        new_device = devices[new_ind]
        new_obj = self.device_manager.audio_dict[new_device]
        if self.audio_disconnect_event.is_set():
            return
        AudioUtilities.SetDefaultDevice(new_device.id)
        self.audio_dev = new_device
        self.audio_obj = new_obj
        self.audio_ind = new_ind
        self.logger.info(f'Переключились на устройство {new_device.FriendlyName}')
        self.msg.notification('🎧 Переключено на:', new_device.FriendlyName, 'change_audio')