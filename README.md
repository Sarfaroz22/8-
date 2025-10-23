import os
import re
from datetime import datetime
import pygame
from pygame import Rect, Surface
from pygame.event import Event

from utils import fetch_resource, load_scaled_image


class Microwave:
    def __init__(
        self,
    ) -> None:
        self.is_running: bool = False
        self.SIZE = self.width, self.height = 1500, 750
        self.BODY_POSITION: tuple[int, int] = (350, 90)
        self.BODY_SIZE: tuple[int, int] = (700, 450)

        self._body: Surface
        self._body_light: Surface

        self._DOOR_OFFSET: tuple[float, float] = (-0.279, -0.144)
        self._DOOR_SIZE_RATIO: tuple[float, float] = (1.014, 1.267)

        self._CLOSED_DOOR_OFFSET: tuple[float, float] = (0.057, 0.056)
        self._CLOSED_DOOR_SIZE_RATIO: tuple[float, float] = (0.671, 0.856)

        self._OPENNED_DOOR_OFFSET: tuple[float, float] = (-0.259, -0.133)
        self._OPENNED_DOOR_SIZE_RATIO: tuple[float, float] = (0.346, 1.236)

        self._DOOR_X_POSITION: int = self.BODY_POSITION[0] - 195
        self._DOOR_Y_POSITION: int = self.BODY_POSITION[1] - 65
        self._door_state = 0
        self._is_door_closed: bool = True
        self._is_door_openning: bool = False
        self._is_door_closing: bool = False
        self._door_frames: list[Surface]

        self._DOOR_RECT, self._closed_door_rect, self._openned_door_rect = (
            self._resize()
        )

        self._is_light_on = False
        # Новые атрибуты состояния (добавлено здесь, после _is_light_on)
        self._current_mode: str = "idle"  # idle, timer, frozen
        self._timer_seconds: int = 0
        self._is_cooking: bool = False
        self._setting_time: bool = False  # Флаг, что мы устанавливаем время

        self._button_data: list[
            tuple[str, tuple[float, float], tuple[float, float], object]
        ]
        self._buttons: list[dict[str, str | Surface | Rect]]
        self._timer_font: pygame.font.SysFont = pygame.font.SysFont("Arial", 74)
        self._timer_text: datetime

        self.initialize_data()

    def _resize(self) -> tuple[Rect, Rect, Rect]:
        bx, by = self.BODY_POSITION
        bw, bh = self.BODY_SIZE

        def rel_rect(
            offset_ratio: tuple[float, float], size_ratio: tuple[float, float]
        ) -> Rect:
            ox, oy = offset_ratio
            sw, sh = size_ratio
            return Rect(
                bx + bw * ox,
                by + bh * oy,
                bw * sw,
                bh * sh,
            )

        return (
            rel_rect(self._DOOR_OFFSET, self._DOOR_SIZE_RATIO),
            rel_rect(self._CLOSED_DOOR_OFFSET, self._CLOSED_DOOR_SIZE_RATIO),
            rel_rect(self._OPENNED_DOOR_OFFSET, self._OPENNED_DOOR_SIZE_RATIO),
        )

    def sort_files_numerically(self, files: list[str]) -> list[str]:
        return sorted(
            files,
            key=lambda name: [
                int(s) if s.isdigit() else s for s in re.split(r"(\d+)", name)
            ],
        )

    def initialize_data(self) -> None:
        frames_folder: str = fetch_resource("door_frames")
        self._door_frames = [
            load_scaled_image(
                os.path.join(frames_folder, file),
                (self._DOOR_RECT.w, self._DOOR_RECT.h),
            )
            for file in self.sort_files_numerically(os.listdir(frames_folder))
            if file.endswith(".png")
        ]

        buttons_folder = fetch_resource("buttons")
        self._button_data = [
            ("timer", (0.75, 0.077), (0.221, 0.144), self.on_timer_click),
            ("frozen", (0.75, 0.26), (0.214, 0.133), self.on_quick_defrost_click),
            ("double_left", (0.74, 0.426), (0.042, 0.084), self.on_double_left_click),
            ("left", (0.787, 0.422), (0.035, 0.088), self.on_left_click),
            ("ok", (0.828, 0.422), (0.057, 0.088), self.on_ok_click),
            ("right", (0.892, 0.422), (0.035, 0.088), self.on_right_click),
            (
                "double_right",
                (0.935, 0.422),
                (0.042, 0.088),
                self.on_double_right_click,
            ),
            ("start", (0.781, 0.555), (0.142, 0.133), self.on_start_click),
            ("stop", (0.781, 0.733), (0.142, 0.133), self.on_stop_click),
        ]
        self._buttons = self._create_buttons(buttons_folder)
        self._body = load_scaled_image(fetch_resource("microwave.png"), self.BODY_SIZE)
        self._body_light = load_scaled_image(
            fetch_resource("microwave_light.png"), self.BODY_SIZE
        )

        self.is_running = True

    def _create_buttons(self, buttons_folder: str):
        bx, by = self.BODY_POSITION
        bw, bh = self.BODY_SIZE

        def rel_to_abs(pos_ratio, size_ratio):
            """Перевод относительных координат и размеров в абсолютные."""
            rx, ry = pos_ratio
            rw, rh = size_ratio
            return (bx + bw * rx, by + bh * ry), (bw * rw, bh * rh)

        buttons = []
        for name, pos_ratio, size_ratio, action in self._button_data:
            pos, size = rel_to_abs(pos_ratio, size_ratio)
            image_path = os.path.join(buttons_folder, f"{name}.png")
            if not os.path.exists(image_path):
                continue

            buttons.append(
                {
                    "name": name,
                    "image": load_scaled_image(image_path, size),
                    "rect": Rect(pos, size),
                    "action": action,
                }
            )
        return buttons

    def get_body(self) -> Surface:
        return self._body_light if self._is_light_on else self._body

    # Обновлённые методы кнопок (заменены на функциональную логику)
    def on_timer_click(self) -> None:
        if not self._is_cooking and self._is_door_closed:
            self._current_mode = "timer"
            self._setting_time = True
            print("Режим установки времени активирован.")

    def on_quick_defrost_click(self) -> None:
        if not self._is_cooking and self._is_door_closed:
            self._current_mode = "frozen"
            self._timer_seconds = 300  # 5 минут по умолчанию для разморозки
            print("Режим быстрой разморозки активирован. Нажмите Start для запуска.")

    def on_double_left_click(self) -> None:
        if self._setting_time:
            self._timer_seconds = max(0, self._timer_seconds - 600)  # Минус 10 минут
            print(f"Время: {self._timer_seconds // 60:02d}:{self._timer_seconds % 60:02d}")

    def on_left_click(self) -> None:
        if self._setting_time:
            self._timer_seconds = max(0, self._timer_seconds - 60)  # Минус 1 минута
            print(f"Время: {self._timer_seconds // 60:02d}:{self._timer_seconds % 60:02d}")

    def on_ok_click(self) -> None:
        if self._setting_time:
            self._setting_time = False
            print("Время подтверждено. Нажмите Start для запуска.")

    def on_right_click(self) -> None:
        if self._setting_time:
            self._timer_seconds += 60  # Плюс 1 минута
            print(f"Время: {self._timer_seconds // 60:02d}:{self._timer_seconds % 60:02d}")

    def on_double_right_click(self) -> None:
        if self._setting_time:
            self._timer_seconds += 600  # Плюс 10 минут
            print(f"Время: {self._timer_seconds // 60:02d}:{self._timer_seconds % 60:02d}")

    def on_start_click(self) -> None:
        if self._timer_seconds > 0 and not self._is_cooking and self._is_door_closed:
            self._is_cooking = True
            self._is_light_on = True  # Зажигаем свет внутри
            print(f"Запуск! Режим: {self._current_mode}. Время: {self._timer_seconds} сек.")

    def on_stop_click(self) -> None:
        if self._is_cooking:
            self._is_cooking = False
            self._is_light_on = False
            self._timer_seconds = 0
            self._current_mode = "idle"
            print("Остановлено.")

    # Обновлённый draw_timer (заменён полностью)
    def draw_timer(self, surface: Surface) -> None:
        if self._is_cooking and self._timer_seconds > 0:
            minutes = self._timer_seconds // 60
            seconds = self._timer_seconds % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            color = (255, 0, 0)  # Красный, когда готовит
        elif self._setting_time:
            minutes = self._timer_seconds // 60
            seconds = self._timer_seconds % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            color = (0, 255, 0)  # Зелёный, когда устанавливаем
        else:
            time_str = "00:00"
            color = (0, 255, 0)

        time_surface = self._timer_font.render(time_str, True, color)
        surface.blit(time_surface, (885, 130))

    # Новый метод update_timer (добавлен после draw_timer)
    def update_timer(self) -> None:
        if self._is_cooking and self._timer_seconds > 0:
            self._timer_seconds -= 1  # Уменьшаем каждую секунду (нужен таймер в игре)
            if self._timer_seconds == 0:
                self._is_cooking = False
                self._current_mode = "idle"
                self._is_light_on = False
                print("Готово! Микроволновка закончила.")

    def draw_buttons(self, surface: Surface) -> None:
        for button in self._buttons:
            surface.blit(button["image"], button["rect"].topleft)  # type: ignore

    def draw_door_hitboxes(self, surface: Surface) -> None:
        pygame.draw.rect(surface, (0, 255, 0), self._closed_door_rect, 2)
        pygame.draw.rect(surface, (0, 255, 0), self._openned_door_rect, 2)

    def draw_door(self, surface: Surface) -> None:
        door: Surface = self._door_frames[self._door_state]
        surface.blit(door, self._DOOR_RECT.topleft)

    def update_door(self) -> None:
        if self._is_door_openning:
            if self._door_state < len(self._door_frames) - 1:
                self._door_state += 1
            else:
                self._is_door_openning = False
        elif self._is_door_closing:
            if self._door_state > 0:
                self._door_state -= 1
            else:
                self._is_door_closing = False
                self._is_door_closed = True

    def on_event(self, event: Event) -> None:
        mx, my = pygame.mouse.get_pos()
        match event.type:
            case pygame.QUIT:
                self.is_running = False
            case pygame.MOUSEBUTTONDOWN:
                for button in self._buttons:
                    if button["rect"].collidepoint(mx, my):  # type: ignore
                        button["action"]()  # type: ignore
                if bool(self._is_door_openning + self._is_door_closing) is True:
                    return
                if self._closed_door_rect.collidepoint(mx, my):
                    self._is_door_closed = False
                    self._is_door_openning = True
                    return
                if self._openned_door_rect.collidepoint(mx, my):
                    self._is_door_closing = True
                    return
