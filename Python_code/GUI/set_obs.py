import tkinter as tk
from tkinter import ttk
import json
import os
import logging

from Python_code.core.config import setup_logger



setup_logger()


class SetOBS:
    def __init__(self, parent):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.window = parent
        self.window = tk.Toplevel(parent)
        self.canvas = None
        self.x = self.window.winfo_screenwidth()
        self.y = self.window.winfo_screenheight()
        self.x_size, self.y_size = 700, 500
        self.icon = tk.PhotoImage(file="data/иконка.png")
        self.style = ttk.Style()

        self.path = 'data/obs_settings.json'
        self.settings_obs = {
            'port': 4455,
            'password': 12345,
            'A': 'Первый канал',
            'B': 'Второй канал',
            'C': 'Третий канал',
            'D': 'Четвёртый канал',
        }
        self.load_settings()

        self.port_entry = None
        self.psw_entry = None

        self.start_customization()
        self.start_uploading_gui()

        self.window.transient(parent)

    def start_customization(self):
        """Стартовая настройка окна"""
        self.window.title('Настройки профиля OBS')
        self.window.geometry(
            f'{self.x_size}x{self.y_size}+{int(self.x / 2 - self.x_size / 2)}+{int(self.y / 2 - self.y_size / 2)}')
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
        ttk.Label(frame, text="Настройки подключения к OBS",
                  font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=3, pady=10)

        # Порт
        ttk.Label(frame, text="Порт:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.port_entry = ttk.Entry(frame, width=15)
        self.port_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        self.port_entry.insert(0, "4455")

        # Пароль
        ttk.Label(frame, text="Пароль:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.psw_entry = ttk.Entry(frame, width=25, show="*")
        self.psw_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # Списки
        ttk.Label(frame, text="Назначение каналов:",
                  font=("Segoe UI", 12)).grid(row=3, column=0, columnspan=3, pady=(20, 10))

        # Канал A
        ttk.Label(frame, text="Канал A:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.entry_a = ttk.Entry(frame, width=25)
        self.entry_a.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        # Канал B
        ttk.Label(frame, text="Канал B:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
        self.entry_b = ttk.Entry(frame, width=25)
        self.entry_b.grid(row=5, column=1, padx=10, pady=5, sticky="w")

        # Канал C
        ttk.Label(frame, text="Канал C:").grid(row=6, column=0, padx=10, pady=5, sticky="e")
        self.entry_c = ttk.Entry(frame, width=25)
        self.entry_c.grid(row=6, column=1, padx=10, pady=5, sticky="w")

        # Канал D
        ttk.Label(frame, text="Канал D:").grid(row=7, column=0, padx=10, pady=5, sticky="e")
        self.entry_d = ttk.Entry(frame, width=25)
        self.entry_d.grid(row=7, column=1, padx=10, pady=5, sticky="w")

        # Кнопка
        ttk.Button(frame, text="Сохранить", command=self.save_settings).grid(
            row=8, column=0, columnspan=2, pady=20
        )

        self.status_label = ttk.Label(frame, text="", foreground="green")
        self.status_label.grid(row=9, column=0, columnspan=2)

        self.display_settings()

    def load_settings(self):
        """Подгружает текущие настройки из файла"""
        if os.path.exists(self.path):
            with open(self.path, 'r', encoding='utf-8') as f:
                self.settings_obs = json.load(f)
            self.logger.info("Загрузили настройки из файла")
        else:
            self.logger.info("Оставили настройки по умолчанию")

    def save_settings(self):
        """Сохраняет настройки из полей ввода"""
        # Собираем данные из полей
        self.settings_obs = {
            'port': self.port_entry.get(),
            'password': self.psw_entry.get(),
            'A': self.entry_a.get(),
            'B': self.entry_b.get(),
            'C': self.entry_c.get(),
            'D': self.entry_d.get(),
        }
        # Сохраняем в файл
        with open(self.path, "w", encoding='utf-8') as f:
            json.dump(self.settings_obs, f, ensure_ascii=False, indent=4)
        self.status_label.config(text="✅ Настройки сохранены!", foreground="green")
        self.logger.info("Настройки OBS сохранены")

    def display_settings(self):
        """Заполняет поля из загруженных настроек"""
        self.port_entry.delete(0, tk.END)
        self.port_entry.insert(0, self.settings_obs.get('port', '4455'))

        self.psw_entry.delete(0, tk.END)
        self.psw_entry.insert(0, self.settings_obs.get('password', ''))

        self.entry_a.delete(0, tk.END)
        self.entry_a.insert(0, self.settings_obs.get('A', ''))

        self.entry_b.delete(0, tk.END)
        self.entry_b.insert(0, self.settings_obs.get('B', ''))

        self.entry_c.delete(0, tk.END)
        self.entry_c.insert(0, self.settings_obs.get('C', ''))

        self.entry_d.delete(0, tk.END)
        self.entry_d.insert(0, self.settings_obs.get('D', ''))