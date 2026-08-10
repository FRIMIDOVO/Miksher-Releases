import tkinter as tk
from tkinter import ttk
import ctypes
import json
import logging

from Python_code.core.config import setup_logger



setup_logger()


class SetBind:
    def __init__(self, parent):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.window = parent
        self.window = tk.Toplevel(parent)
        self.canvas = None
        self.x = self.window.winfo_screenwidth()
        self.y = self.window.winfo_screenheight()
        self.x_size, self.y_size = 1200, 500
        self.icon = tk.PhotoImage(file="data/иконка.png")
        self.style = ttk.Style()

        self.path = 'data/binds.json'
        self.binds = {

        }

        self.cash_load()
        self.start_customization()
        self.start_uploading_gui()
        self.start_uploading_interface()

        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.window.transient(parent)

    def start_customization(self):
        """Стартовая настройка окна"""
        self.window.title('Настройки биндов')
        self.window.geometry(f'{self.x_size}x{self.y_size}+{int(self.x / 2 - self.x_size / 2)}+{int(self.y / 2 - self.y_size / 2)}')
        self.window.minsize(self.x_size, self.y_size)
        self.window.resizable(False, False)
        self.window.iconphoto(True, self.icon)
        self.style.theme_use('vista')
        self.style.configure('TCheckbutton', font=('Segoe UI', 15))
        self.canvas = tk.Canvas(self.window, width=self.x_size, height=self.y_size, bg='#5B6C87', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

    def start_uploading_gui(self):
        """Стартовая генерация интерфейса"""

        # ==================== НАСТРОЙКИ ЦВЕТОВ ====================
        COLORS = {
            # Фоны
            'canvas_bg': '#5B6C87',  # фон всего окна
            'main_rect_fill': '#e0e0e0',  # фон большого прямоугольника
            'main_rect_outline': '#aaaaaa',  # обводка большого прямоугольника
            'btn_fill': '#d0d0d0',  # фон кнопок (квадраты и круги)
            'btn_outline': '#888888',  # обводка кнопок
            'line_rect_fill': '#c0c0c0',  # фон маленьких прямоугольников на линиях
            'line_rect_outline': '#999999',  # обводка маленьких прямоугольников

            # Линии и стрелки
            'line_color': '#888888',  # цвет вертикальных линий
            'arrow_color': '#5B6C87',  # цвет стрелок и точки

            # Текст
            'text_color': '#5B6C87',  # цвет цифр и букв
        }
        # ==========================================================

        # Базовые координаты и размеры (абсолютные, всё от них пляшет)
        base_x = 150
        base_y = 50
        rect_width = 550
        rect_height = 400

        # Координаты белого прямоугольника
        x1 = base_x
        y1 = base_y
        x2 = x1 + rect_width
        y2 = y1 + rect_height

        # Очищаем canvas и задаём фон
        self.canvas.delete("all")
        self.canvas.configure(bg=COLORS['canvas_bg'])

        # Рисуем прямоугольник
        self.canvas.create_rectangle(x1, y1, x2, y2,
                                     fill=COLORS['main_rect_fill'],
                                     outline=COLORS['main_rect_outline'],
                                     width=2,
                                     tags='main_rect')

        # Параметры элементов
        h = rect_height
        button_size = int(h * 0.186)
        left_margin = int(h * 0.1)
        button_spacing = int(h * 0.08)

        # === ВЕРТИКАЛЬНЫЕ ЛИНИИ ===
        line_height = int(h * 0.75)
        line_y1 = y1 + (rect_height - line_height) // 2
        line_y2 = line_y1 + line_height

        line_spacing = int(h * 0.2)
        center_x = x1 + (rect_width // 2)

        line_x_positions = [
            center_x - line_spacing,
            center_x,
            center_x + line_spacing
        ]

        rect_height_line = int(h * 0.23)
        rect_width_line = int(h * 0.1)

        for i, line_x in enumerate(line_x_positions):
            self.canvas.create_line(line_x, line_y1, line_x, line_y2,
                                    fill=COLORS['line_color'], width=2, smooth=True,
                                    tags=f'vertical_line_{i}')

            if i == 0:
                rect_y = line_y1 + 10
            elif i == 1:
                rect_y = line_y2 - rect_height_line - 10
            else:
                rect_y = line_y1 + (line_height - rect_height_line) // 2

            self.canvas.create_rectangle(
                line_x - rect_width_line // 2,
                rect_y,
                line_x + rect_width_line // 2,
                rect_y + rect_height_line,
                fill=COLORS['line_rect_fill'],
                outline=COLORS['line_rect_outline'],
                width=1,
                tags=f'line_rect_{i}'
            )

        center_y = y1 + (rect_height // 2)

        middle_y = center_y - (button_size // 2)
        top_y = middle_y - button_size - button_spacing
        bottom_y = middle_y + button_size + button_spacing

        # === ЛЕВАЯ СТОРОНА ===
        button_x_left = x1 + left_margin

        # Левые квадраты
        for i, (name, y_pos) in enumerate([('1', top_y), ('2', middle_y), ('3', bottom_y)]):
            self.canvas.create_rectangle(button_x_left, y_pos,
                                         button_x_left + button_size, y_pos + button_size,
                                         fill=COLORS['btn_fill'], outline=COLORS['btn_outline'], width=2,
                                         tags=f'button_left_{i}')

            self.canvas.create_text(button_x_left + button_size // 2, y_pos + button_size // 2,
                                    text=name, font=('Segoe UI', int(button_size * 0.35), 'normal'),
                                    fill=COLORS['text_color'], anchor='center')

        # === ПРАВАЯ СТОРОНА ===
        button_x_right = x2 - left_margin - button_size

        # Правый верхний квадрат с цифрой 4
        self.canvas.create_rectangle(button_x_right, top_y,
                                     button_x_right + button_size, top_y + button_size,
                                     fill=COLORS['btn_fill'], outline=COLORS['btn_outline'], width=2,
                                     tags='button_right_top')
        self.canvas.create_text(button_x_right + button_size // 2, top_y + button_size // 2,
                                text='4', font=('Segoe UI', int(button_size * 0.35), 'normal'),
                                fill=COLORS['text_color'], anchor='center')

        # Средний круг (крестовина)
        cx = button_x_right + button_size // 2
        cy = middle_y + button_size // 2
        r = button_size // 2 - 4

        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                fill=COLORS['btn_fill'], outline=COLORS['btn_outline'], width=2,
                                tags='button_right_middle')

        # Стрелки
        arrow_len = int(r * 0.4)
        arrow_width = 2

        self.canvas.create_line(cx, cy - arrow_len, cx, cy - r + 5,
                                fill=COLORS['arrow_color'], width=arrow_width, arrow='last', smooth=True)
        self.canvas.create_line(cx, cy + arrow_len, cx, cy + r - 5,
                                fill=COLORS['arrow_color'], width=arrow_width, arrow='last', smooth=True)
        self.canvas.create_line(cx - arrow_len, cy, cx - r + 5, cy,
                                fill=COLORS['arrow_color'], width=arrow_width, arrow='last', smooth=True)
        self.canvas.create_line(cx + arrow_len, cy, cx + r - 5, cy,
                                fill=COLORS['arrow_color'], width=arrow_width, arrow='last', smooth=True)

        # Точка по центру
        dot_r = 3
        self.canvas.create_oval(cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r,
                                fill=COLORS['arrow_color'], outline=COLORS['arrow_color'],
                                tags='button_right_middle_dot')

        # Нижний круг с буквой A
        self.canvas.create_oval(button_x_right, bottom_y,
                                button_x_right + button_size, bottom_y + button_size,
                                fill=COLORS['btn_fill'], outline=COLORS['btn_outline'], width=2,
                                tags='button_right_bottom')
        self.canvas.create_text(button_x_right + button_size // 2, bottom_y + button_size // 2,
                                text='A', font=('Segoe UI', int(button_size * 0.35), 'normal'),
                                fill=COLORS['text_color'], anchor='center')

        # === БУКВЫ НА ПРЯМОУГОЛЬНИКАХ ПО ЦЕНТРУ (B, C, D) ===
        font_size = int(rect_height_line * 0.35)

        # B — левая линия
        rect1_x = line_x_positions[0]
        rect1_y = line_y1 + 10 + rect_height_line // 2
        self.canvas.create_text(rect1_x, rect1_y,
                                text='B', font=('Segoe UI', font_size, 'normal'),
                                fill=COLORS['text_color'], anchor='center')

        # C — центральная линия
        rect2_x = line_x_positions[1]
        rect2_y = line_y2 - rect_height_line - 10 + rect_height_line // 2
        self.canvas.create_text(rect2_x, rect2_y,
                                text='C', font=('Segoe UI', font_size, 'normal'),
                                fill=COLORS['text_color'], anchor='center')

        # D — правая линия
        rect3_x = line_x_positions[2]
        rect3_y = line_y1 + (line_height - rect_height_line) // 2 + rect_height_line // 2
        self.canvas.create_text(rect3_x, rect3_y,
                                text='D', font=('Segoe UI', font_size, 'normal'),
                                fill=COLORS['text_color'], anchor='center')

    def start_uploading_interface(self):
        """Прогрузка интерфейса с выпадающими списками"""

        # ==================== НАСТРОЙКИ ЦВЕТОВ ====================
        COLORS = {
            'canvas_bg': '#5B6C87',
            'text_color': '#e0e0e0',
        }
        # ==========================================================

        # Базовые координаты и размеры
        base_x = 150
        base_y = 50
        rect_width = 550
        rect_height = 400

        x1 = base_x
        y1 = base_y
        x2 = x1 + rect_width
        y2 = y1 + rect_height

        # Значения для выпадающих списков
        action_values_butt = [
            'Без функции',
            'Следующий трек',
            'Предыдущий трек',
            'Play / Pause',
            'Мут звука',
            'Мут микрофона'
        ]

        action_values_pot = [
            'Без функции',
            'Громкость системы',
            'Громкость приложения',
            'Громкость канала OBS'
        ]

        action_values_encoder = [
            'Без функции',
            'Листание окон'
        ]

        # Элементы для левого столбца
        left_elements = [
            ('1', 'butt'),
            ('2', 'butt'),
            ('3', 'butt'),
            ('4', 'butt'),
            ('A', 'pot'),
            ('B', 'pot'),
            ('C', 'pot'),
            ('D', 'pot'),
        ]

        # Элементы для правого столбца
        right_elements = [
            ('Энкодер', 'encoder'),
            ('↑', 'butt'),
            ('↓', 'butt'),
            ('←', 'butt'),
            ('→', 'butt'),
            ('●', 'butt'),
        ]

        # Координаты
        col1_x = x2 + 50
        col1_combo_x = col1_x + 8
        col2_x = col1_x + 250
        col2_combo_x = col2_x + 8
        start_y = 80
        list_spacing = 45

        self.element_combos = {}

        # Левый столбец
        for i, (label, elem_type) in enumerate(left_elements):
            y_pos = start_y + i * list_spacing

            if elem_type == 'butt':
                values = action_values_butt
            else:
                values = action_values_pot

            self.canvas.create_text(col1_x, y_pos - 12,
                                    text=label, font=('Segoe UI', 11, 'bold'),
                                    fill=COLORS['text_color'], anchor='e')

            combo = ttk.Combobox(self.canvas, values=values, state='readonly', width=20)
            combo.set('Без функции')
            combo.bind('<FocusIn>', lambda e: self.canvas.focus_set())
            self.canvas.create_window(col1_combo_x, y_pos - 10, window=combo, anchor='w')
            self.element_combos[f'left_{label}'] = combo

        # Правый столбец
        for i, (label, elem_type) in enumerate(right_elements):
            y_pos = start_y + i * list_spacing

            if elem_type == 'butt':
                values = action_values_butt
            elif elem_type == 'encoder':
                values = action_values_encoder
            else:
                values = action_values_butt

            self.canvas.create_text(col2_x, y_pos - 12,
                                    text=label, font=('Segoe UI', 11, 'bold'),
                                    fill=COLORS['text_color'], anchor='e')

            combo = ttk.Combobox(self.canvas, values=values, state='readonly', width=20)
            combo.set('Без функции')
            combo.bind('<FocusIn>', lambda e: self.canvas.focus_set())
            self.canvas.create_window(col2_combo_x, y_pos - 10, window=combo, anchor='w')
            self.element_combos[f'right_{label}'] = combo

        # === КНОПКА СОХРАНИТЬ ===
        button_y = start_y + len(right_elements) * list_spacing
        save_btn = tk.Button(self.window, text="Сохранить",
                             command=self.save_binds,
                             font=('Segoe UI', 10),
                             bg='#e0e0e0', fg='#333333',
                             padx=15, pady=4,
                             relief='raised', bd=1,
                             cursor='hand2')
        self.canvas.create_window(col2_combo_x, button_y - 10, window=save_btn, anchor='w')

    def save_binds(self):
        """Сохраняет настройки биндов в JSON"""
        binds_data = {}

        # Собираем значения из всех комбобоксов
        for key, combo in self.element_combos.items():
            value = combo.get()
            if value != 'Без функции':
                binds_data[key] = value
            else:
                binds_data[key] = None

        # Сохраняем в файл
        try:
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(binds_data, f, ensure_ascii=False, indent=4)
            self.logger.info(f"Настройки сохранены в {self.path}")

            # Показываем уведомление
            self.status_label = tk.Label(self.window, text="✅ Настройки сохранены!",
                                         font=('Segoe UI', 10), fg='green', bg='#5B6C87')
            self.status_label.place(relx=0.5, y=500, anchor='center')
            self.window.after(2000, lambda: self.status_label.destroy())

        except Exception as e:
            self.logger.error(f"Ошибка сохранения: {e}")
            self.status_label = tk.Label(self.window, text="❌ Ошибка сохранения!",
                                         font=('Segoe UI', 10), fg='red', bg='#5B6C87')
            self.status_label.place(relx=0.5, y=500, anchor='center')
            self.window.after(2000, lambda: self.status_label.destroy())

    def cash_load(self):
        """Загрузка биндов из файла"""
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                binds_data = json.load(f)

            # Восстанавливаем значения в комбобоксах
            for key, value in binds_data.items():
                if key in self.element_combos and value is not None:
                    self.element_combos[key].set(value)

            self.logger.info(f"Настройки загружены из {self.path}")
        except FileNotFoundError:
            self.logger.info("Файл с настройками не найден, используем значения по умолчанию")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки: {e}")

    def cash_load(self):
        """Загрузка хэша из файла"""


    def cash_save(self):
        """Сохраняет текущие бинды в JSON"""


    def on_close(self):
        """При закрытии окна сохраняем бинды и закрываемся"""
        self.cash_save()
        self.window.destroy()