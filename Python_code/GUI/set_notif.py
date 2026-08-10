import tkinter as tk
from tkinter import ttk
import json
import os
import logging

from Python_code.core.config import setup_logger

setup_logger()

class SetNotif:
    def __init__(self, parent):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.canvas = None
        self.x = self.window.winfo_screenwidth()
        self.y = self.window.winfo_screenheight()
        self.x_size, self.y_size = 700, 500
        self.icon = tk.PhotoImage(file="data/иконка.png")
        self.style = ttk.Style()

        self.path = 'data/not_settings.json'
        self.settings = {
            'connection_not': True,
            'disconnection_not': True,
            'change_audio_not': True,
            'bind_not': True,
            'sound_not': True
        }

        self.connection_not = tk.BooleanVar(value=True)
        self.disconnection_not = tk.BooleanVar(value=True)
        self.change_audio_not = tk.BooleanVar(value=True)
        self.bind_not = tk.BooleanVar(value=True)
        self.sound_not = tk.BooleanVar(value=True)

        self.load_settings()
        self.start_customization()
        self.start_uploading_gui()

        self.window.transient(parent)

    def start_customization(self):
        """Стартовая настройка окна"""
        self.window.title('Настройки уведомлений')
        self.window.geometry(f'{self.x_size}x{self.y_size}+{int(self.x / 2 - self.x_size / 2)}+{int(self.y / 2 - self.y_size / 2)}')
        self.window.minsize(self.x_size, self.y_size)
        self.window.resizable(False, False)
        self.window.iconphoto(True, self.icon)
        self.style.theme_use('vista')
        self.style.configure('TCheckbutton', font=('Segoe UI', 15))
        self.canvas = tk.Canvas(self.window, width=self.x_size, height=self.y_size, bg='#5B6C87', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

    def start_uploading_gui(self):
        # Создаём центральный фрейм
        frame = ttk.Frame(self.window)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        # Заголовок
        ttk.Label(frame, text="Настройки уведомлений",
                  font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        # Чекбоксы
        check_connection_not = ttk.Checkbutton(frame, text='Уведомления о подключении контроллера',
                                                variable=self.connection_not, takefocus=False)
        check_connection_not.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        check_disconnection_not = ttk.Checkbutton(frame, text='Уведомления об отключении контроллера',
                                                  variable=self.disconnection_not, takefocus=False)
        check_disconnection_not.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        check_change_audio_not = ttk.Checkbutton(frame, text='Уведомление о смене устройства',
                                                 variable=self.change_audio_not, takefocus=False)
        check_change_audio_not.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        bind_not = ttk.Checkbutton(frame, text='Уведомление о новых биндах',
                                   variable=self.bind_not, takefocus=False)
        bind_not.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        check_sound_not = ttk.Checkbutton(frame, text='Звук уведомлений',
                                          variable=self.sound_not, takefocus=False)
        check_sound_not.grid(row=5, column=0, padx=10, pady=5, sticky="w")

        # Кнопка сохранить
        ttk.Button(frame, text="Сохранить", command=self.save_settings).grid(
            row=6, column=0, columnspan=2, pady=20
        )

        self.status_label = ttk.Label(frame, text="", foreground="green")
        self.status_label.grid(row=7, column=0, columnspan=2)

        self.display_settings()

    def load_settings(self):
        """Подгружает текущие настройки из файла"""
        if os.path.exists(self.path):
            with open(self.path, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
            self.logger.info("Загрузили настройки из файла")
        else:
            self.logger.info("Оставили настройки по умолчанию")

    def save_settings(self):
        """Сохраняет текущие значения в JSON"""
        self.settings = {
            'connection_not': self.connection_not.get(),
            'disconnection_not': self.disconnection_not.get(),
            'change_audio_not': self.change_audio_not.get(),
            'bind_not': self.bind_not.get(),
            'sound_not': self.sound_not.get()
        }
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=4)
        self.status_label.config(text="✅ Настройки сохранены!", foreground="green")
        self.logger.info("Настройки сохранены")

    def display_settings(self):
        """Заполняет поля из загруженных настроек"""
        self.connection_not.set(self.settings.get('connection_not', True))
        self.disconnection_not.set(self.settings.get('disconnection_not', True))
        self.change_audio_not.set(self.settings.get('change_audio_not', True))
        self.bind_not.set(self.settings.get('bind_not', True))
        self.sound_not.set(self.settings.get('sound_not', True))