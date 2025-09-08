import tkinter as tk
from tkinter import messagebox
import math

class PieChartApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pie Chart Input")

        # Поле для ввода меток (через запятую)
        tk.Label(self.root, text="Введите метки (через запятую):").pack()
        self.labels_entry = tk.Entry(self.root, width=50)
        self.labels_entry.pack()

        # Поле для ввода значений (через запятую)
        tk.Label(self.root, text="Введите значения (через запятую):").pack()
        self.values_entry = tk.Entry(self.root, width=50)
        self.values_entry.pack()

        # Кнопка для построения диаграммы
        self.draw_button = tk.Button(self.root, text="Построить диаграмму", command=self.on_draw)
        self.draw_button.pack(pady=10)

        # Canvas для рисования диаграммы
        self.canvas = tk.Canvas(self.root, width=500, height=400)
        self.canvas.pack()

    def on_draw(self):
        labels_text = self.labels_entry.get().strip()
        values_text = self.values_entry.get().strip()

        if not labels_text or not values_text:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните оба поля.")
            return

        labels = [label.strip() for label in labels_text.split(",")]
        values_str = [v.strip() for v in values_text.split(",")]

        if len(labels) != len(values_str):
            messagebox.showerror("Ошибка", "Количество меток и значений должно совпадать.")
            return

        try:
            values = [float(v) for v in values_str]
        except ValueError:
            messagebox.showerror("Ошибка", "Значения должны быть числами.")
            return

        if any(v < 0 for v in values):
            messagebox.showerror("Ошибка", "Значения должны быть неотрицательными.")
            return

        data = dict(zip(labels, values))
        if sum(values) == 0:
            messagebox.showerror("Ошибка", "Сумма значений должна быть больше нуля.")
            return

        self.draw_pie_chart(data)

    def draw_pie_chart(self, data_dict):
        self.canvas.delete("all")
        total = sum(data_dict.values())

        radius = 150
        center_x = 250
        center_y = 200

        start_angle = 0

        colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta', 'yellow', 'brown', 'pink']

        for i, (label, value) in enumerate(data_dict.items()):
            extent_angle = (value / total) * 360
            color = colors[i % len(colors)]

            self.canvas.create_arc(
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
                start=start_angle,
                extent=extent_angle,
                fill=color,
                outline='black'
            )

            mid_angle_rad = math.radians(start_angle + extent_angle / 2)
            label_x = center_x + (radius / 2) * math.cos(mid_angle_rad)
            label_y = center_y - (radius / 2) * math.sin(mid_angle_rad)

            percentage_text = f"{label}\n{(value / total) * 100:.1f}%"
            self.canvas.create_text(label_x, label_y, text=percentage_text, fill='black')

            start_angle += extent_angle

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = PieChartApp()
    app.run()
