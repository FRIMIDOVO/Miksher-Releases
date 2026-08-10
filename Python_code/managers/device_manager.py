import threading
from pycaw.constants import EDataFlow, DEVICE_STATE
import logging
from threading import Thread
import time
from pycaw.pycaw import AudioUtilities
import warnings
import pythoncom

from Python_code.core.config import setup_logger



setup_logger()


class DeviceManager:
    def __init__(self, disconnect_event):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.disconnect_event = disconnect_event
        self.audio_dict = {}  # {device: interface}
        self.audio_disconnect_event = threading.Event()
        self.audio_disconnect_event.set()
        self.mic_dict = {}  # {device: interface}
        self.mic_disconnect_event = threading.Event()
        self.mic_disconnect_event.set()
        self.cash_len_mic = 0
        self.cash_len_audio = 0
        thread = Thread(target=self.update_devs, daemon=True)
        thread.start() # поток обновляющий список действующих устройств

    def update_devs(self):
        """Поточная функция для обновления списков устройств"""
        pythoncom.CoInitialize()
        try:
            while True:
                try:
                    if not self.disconnect_event.is_set():
                        curr_len_audio = len(AudioUtilities.GetAllDevices(
                            data_flow=EDataFlow.eRender.value,
                            device_state=DEVICE_STATE.ACTIVE.value
                        ))
                        if curr_len_audio != self.cash_len_audio:
                            self.get_audio_devs()
                            self.cash_len_audio = curr_len_audio

                        curr_len_mic = len(AudioUtilities.GetAllDevices(
                            data_flow=EDataFlow.eCapture.value,
                            device_state=DEVICE_STATE.ACTIVE.value
                        ))
                        if curr_len_mic != self.cash_len_mic:
                            self.get_mic_devs()
                            self.cash_len_mic = curr_len_mic
                except Exception as e:
                    self.logger.warning(f"Ошибка обновления: {e}")
                time.sleep(3)
        finally:
            pythoncom.CoUninitialize()

    def get_audio_devs(self):
        """Обновляет список аудио устройств"""
        self.audio_dict.clear()
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                devices = AudioUtilities.GetAllDevices(
                    data_flow=EDataFlow.eRender.value,
                    device_state=DEVICE_STATE.ACTIVE.value
                )
            for device in devices:
                self.audio_dict[device] = self._get_volume_interface(device)
            names = [d.FriendlyName for d in self.audio_dict.keys()]
            if names:
                self.audio_disconnect_event.clear()
                self.logger.info(f'Обновлён список аудио устройств:\n' + '\n'.join(names))
            else:
                self.audio_disconnect_event.set()
                self.logger.info(f'Нет активных аудио устройств')
        except:
            self.cash_len_audio = 0
            self.logger.error('Нет активных аудио устройств')

    def get_mic_devs(self):
        """Обновляет список микрофонных устройств"""
        try:
            self.mic_dict.clear()
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                devices = AudioUtilities.GetAllDevices(
                    data_flow=EDataFlow.eCapture.value,
                    device_state=DEVICE_STATE.ACTIVE.value
                )
            for device in devices:
                self.mic_dict[device] = self._get_volume_interface(device)
            names = [d.FriendlyName for d in self.mic_dict.keys()]
            if names:
                self.mic_disconnect_event.clear()
                self.logger.info(f'Обновлён список микрофонов:\n' + '\n'.join(names))
            else:
                self.mic_disconnect_event.set()
                self.logger.info(f'Нет активных микрофонных устройств')
        except:
            self.cash_len_mic = 0
            self.logger.error('Нет активных микрофонных устройств')

    def _get_volume_interface(self, device):
        """Активирует интерфейс громкости для устройства"""
        try:
            return device.EndpointVolume
        except Exception as e:
            self.logger.error(f"Ошибка: {e}")
            return None