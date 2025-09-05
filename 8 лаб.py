import tkinter as tk
import math

class PieChartApp:
    def __init__(self):

        self.root = tk.Tk()
        self.root.title("Pie Chart")
        self.canvas = tk.Canvas(self.root, width=500, height=400)
        self.canvas.pack()

        # пример данных
        self.data = {
            'A': 30,
            'B': 20,
            'C': 50,
        }

        self.draw_pie_chart(self.data)

    def draw_pie_chart(self, data_dict):
        if not data_dict:
            return

        self.canvas.delete("all")
        total = sum(data_dict.values())

        radius = 150
        center_x = 250
        center_y = 200

        start_angle = 0

        colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta']

        for i, (label, value) in enumerate(data_dict.items()):
            extent_angle = (value / total) * 360

            color = colors[i % len(colors)]

            # Рисуем сектор
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

            # Подписи
            mid_angle_rad = math.radians(start_angle + extent_angle / 2)
            label_x = center_x + (radius / 2) * math.cos(mid_angle_rad)
            label_y = center_y - (radius / 2) * math.sin(mid_angle_rad)

            percentage_text = f"{label}\n{(value / total) * 100:.1f}%"
            self.canvas.create_text(
                label_x,
                label_y,
                text=percentage_text,
                fill='black'
            )

            start_angle += extent_angle

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = PieChartApp()
    app.run()
