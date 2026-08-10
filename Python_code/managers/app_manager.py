import time
from pycaw.pycaw import AudioUtilities, IAudioMeterInformation
import logging
import json
from threading import Thread
import ctypes
import psutil
import pythoncom

from Python_code.core.config import setup_logger



setup_logger()


class AppManager:
    def __init__(self, disconnect_event, msg):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.disconnect_event = disconnect_event
        self.msg = msg
        self.apps = {
            'B': None,
            'C': None,
            'D': None
        }
        self.sessions = {
            'B': None,
            'C': None,
            'D': None
        }
        self.path = 'data/mus.json'
        self.load_hash()
        self.cash_len = 0
        thread = Thread(target=self.check_sessions, daemon=True)
        thread.start() # поток обновляющий список аудио сессий приложений

    def check_sessions(self):
        """При появлении или закрытии сессии обновляет список объектов сессий"""
        pythoncom.CoInitialize()
        try:
            while True:
                try:
                    sessions_len = len(AudioUtilities.GetAllSessions())
                    if sessions_len != self.cash_len and not self.disconnect_event.is_set():
                        self.update_sessions()
                        self.cash_len = sessions_len
                except Exception as e:
                    self.logger.debug(f"Ошибка получения сессий: {e}")
                time.sleep(5)
        finally:
            pythoncom.CoUninitialize()

    def update_sessions(self):
        """Обновляет словарь с объектами аудио сессий"""
        self.logger.debug("Обновление аудио сессий...")
        try:
            # Получаем все активные аудио сессии
            all_sessions = AudioUtilities.GetAllSessions()
        except:
            self.logger.error('Нет активных аудиосессий')
            return
        # Временный словарь для поиска
        temp_sessions = {key: None for key in self.apps.keys()}

        for key, app_name in self.apps.items():
            if not app_name:
                continue

            # Ищем сессию с нужным именем процесса
            found_sessions = []
            for session in all_sessions:
                try:
                    if session.Process and session.Process.name().lower() == app_name.lower():
                        # Получаем интерфейс громкости
                        volume = session.SimpleAudioVolume
                        found_sessions.append((session, volume))
                except Exception as e:
                    self.logger.error(f"Ошибка при проверке сессии: {e}")

            if not found_sessions:
                self.logger.warning(f"Приложение {app_name} не найдено")
                temp_sessions[key] = None
                continue

            # Если нашли несколько сессий - ищем активную
            if len(found_sessions) > 1:
                found_active = False
                for session, volume in found_sessions:
                    try:
                        # Проверяем, воспроизводит ли что-то приложение
                        meter = session._ctl.QueryInterface(IAudioMeterInformation)
                        if meter.GetPeakValue() > 0:
                            temp_sessions[key] = volume
                            found_active = True
                            self.logger.debug(f"Выбрана активная сессия для {app_name}")
                            break
                    except:
                        continue

                if not found_active:
                    temp_sessions[key] = found_sessions[0][1]
                    self.logger.debug(f"Выбрана первая сессия для {app_name}")
            else:
                temp_sessions[key] = found_sessions[0][1]
                self.logger.debug(f"Найдена сессия для {app_name}")

        # Обновляем основной словарь
        self.sessions = temp_sessions
        self.logger.debug("Обновление сессий завершено")

    def load_hash(self):
        """При запуске загружает хэш с именами биндов приложений"""
        try:
            with open(self.path, 'x', encoding='utf-8') as f:
                json.dump(self.apps, f, ensure_ascii=False, indent=4)
                self.logger.info(f"Создан новый файл {self.path}")
        except FileExistsError:
            pass
        with open(self.path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.apps.update(data)
            app_names = [str(app) if app is not None else "None" for app in data.values()]
            self.logger.info(f'Загружены приложения:\n' + '\n'.join(app_names))

    def bind(self, key):
        """Обновляет определёный бинд в файле"""
        app = self.get_active_app()
        self.apps[key] = app
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self.apps, f, ensure_ascii=False, indent=4)
            self.logger.info(f'Обновлен бинд {key}: {app}')
            self.msg.notification(f'🎶 Обновлён бинд {key}:', app, 'new_bind')
        self.update_sessions()

    def get_active_app(self):
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        pid = ctypes.c_ulong()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        try:
            return psutil.Process(pid.value).name().lower()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            self.logger.error('Ошибка при получении активного окна')
            return None