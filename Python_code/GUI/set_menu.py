import tkinter as tk
from tkinter import ttk
import ctypes
import logging

from Python_code.core.config import setup_logger
from Python_code.GUI.set_notif import SetNotif
from Python_code.GUI.set_bind import SetBind
from Python_code.GUI.set_obs import SetOBS



setup_logger()


class SetMenu:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.root = tk.Tk()
        self.style = ttk.Style()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Miksher.Settings")

        self.icon = tk.PhotoImage(file="data/иконка.png")
        self.x = self.root.winfo_screenwidth()
        self.y = self.root.winfo_screenheight()
        self.x_size, self.y_size = 500, 300

        self.settings = None
        self.binds = None
        self.obs = None

        self.start_customization()
        self.start_uploading()
        self.root.mainloop()

    def start_customization(self):
        """Стартовая настройка окна"""
        self.root.configure(bg='#5B6C87')
        self.root.title('Настройки')
        self.root.geometry(f'{self.x_size}x{self.y_size}+{int(self.x / 2 - self.x_size / 2)}+{int(self.y / 2 - self.y_size / 2)}')
        self.root.minsize(self.x_size, self.y_size)
        self.root.resizable(False, False)
        self.root.iconphoto(True, self.icon)
        self.style.theme_use('vista')
        self.style.configure('TCheckbutton', font=('Segoe UI', 15))

    def start_uploading(self):
        """Стартовая генерация интерфейса"""
        title_label = tk.Label(
            self.root,
            text="Настройки",
            font=("Segoe UI", 16, "bold"),
            bg='#5B6C87',  # фон как у окна
            fg='#A3B4CE'  # цвет текста
        )
        title_label.pack(pady=(50, 10))
        button_set_notif = ttk.Button(self.root, text="Настройки уведомлений", command=self.open_settings_not)
        button_set_bind = ttk.Button(self.root, text="Настройки биндов", command=self.open_settings_bind)
        button_set_obs = ttk.Button(self.root, text="Настройки профиля для OBS", command=self.open_settings_obs)
        lst_wid = [button_set_bind, button_set_notif, button_set_obs]
        for wid in lst_wid:
            wid.pack(padx=50, pady=15)

    def open_settings_not(self):
        if self.settings is None or not self.settings.window.winfo_exists():
            self.settings = SetNotif(self.root)
        else:
            self.settings.window.lift()  # поднять окно наверх, если уже открыто

    def open_settings_bind(self):
        if self.binds is None or not self.binds.window.winfo_exists():
            self.binds = SetBind(self.root)
        else:
            self.binds.window.lift()

    def open_settings_obs(self):
        if self.obs is None or not self.obs.window.winfo_exists():
            self.obs = SetOBS(self.root)
        else:
            self.obs.window.lift()