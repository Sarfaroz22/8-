import tkinter as tk
from tkinter import messagebox
import math
from datetime import datetime

# Предположим, у нас есть такие договоры
contracts = [
    {"client": "Иванов", "start_date": "2024-01-01", "end_date": "2024-06-01"},
    {"client": "Петров", "start_date": "2024-03-15", "end_date": "2025-03-14"},
    {"client": "Сидоров", "start_date": "2024-05-01", "end_date": "2024-12-01"},
    {"client": "Иванов", "start_date": "2023-11-01", "end_date": "2024-10-31"},
    {"client": "Петров", "start_date": "2024-07-01", "end_date": "2024-09-30"},
    # добавьте больше для теста
]

class ContractAnalysisApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Анализ договоров аренды")

        # Кнопки для вызова функций
        tk.Button(self.root, text="Анализ по срокам аренды", command=self.segment_by_duration).pack(pady=10)
        tk.Button(self.root, text="Анализ по клиентам", command=self.segment_by_clients).pack(pady=10)

        # Canvas для отображения
        self.canvas = tk.Canvas(self.root, width=600, height=450)
        self.canvas.pack()

    def segment_by_duration(self):
        # Категории длительности (в месяцах)
        categories = {
            "<6 месяцев": 0,
            "6-12 месяцев": 0,
            ">12 месяцев": 0
        }

        today = datetime.today()
        for contract in contracts:
            start_date = datetime.strptime(contract["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(contract["end_date"], "%Y-%m-%d")
            duration_days = (end_date - start_date).days
            duration_months = duration_days / 30  # примерно

            if duration_months < 6:
                categories["<6 месяцев"] += 1
            elif 6 <= duration_months <= 12:
                categories["6-12 месяцев"] += 1
            else:
                categories[">12 месяцев"] += 1

        self.draw_pie_chart(categories)

    def segment_by_clients(self):
        # Подсчет количества договоров по клиентам
        client_counts = {}
        for contract in contracts:
            client = contract["client"]
            client_counts[client] = client_counts.get(client, 0) + 1

        self.draw_pie_chart(client_counts)

    def draw_pie_chart(self, data_dict):
        self.canvas.delete("all")
        total = sum(data_dict.values())

        radius = 200
        center_x = 300
        center_y = 225
        start_angle = 0

        colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta', 'yellow', 'brown', 'pink']

        for i, (label, value) in enumerate(data_dict.items()):
            extent_angle = (value / total) * 360
            color = colors[i % len(colors)]

            self.canvas.create_arc(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                start=start_angle, extent=extent_angle,
                fill=color, outline='black'
            )

            # Положение текста
            mid_angle_rad = math.radians(start_angle + extent_angle / 2)
            label_x = center_x + (radius / 2) * math.cos(mid_angle_rad)
            label_y = center_y - (radius / 2) * math.sin(mid_angle_rad)

            percentage = (value / total) * 100
            text = f"{label}\n{percentage:.1f}%"
            self.canvas.create_text(label_x, label_y, text=text, fill='black', font=("Arial", 9), justify='center')

            start_angle += extent_angle

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ContractAnalysisApp()
    app.run()
