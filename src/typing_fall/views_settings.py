from __future__ import annotations

import arcade

from src.typing_fall.constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    BG_COLOR,
    TEXT_COLOR,
    SUBTEXT_COLOR,
    ACCENT_COLOR,
)
from src.typing_fall.ui_models import Router, MODE_ENDLESS, MODE_TIMED


class SettingsView(arcade.View):
    """Экран настроек: язык, сложность, режим, длительность."""

    def __init__(self, router: Router):
        super().__init__()
        self.router = router

        self.title_text = arcade.Text(
            "Настройки",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT * 0.72,
            TEXT_COLOR,
            font_size=40,
            anchor_x="center",
        )

    def on_show_view(self):
        arcade.set_background_color(BG_COLOR)

    def on_draw(self):
        self.clear()
        self.title_text.draw()

        s = self.router.session.settings
        mode_name = "Бесконечная" if s.mode == MODE_ENDLESS else "По времени"

        arcade.draw_text(
            f"Игрок: {self.router.session.nickname}",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT * 0.62,
            ACCENT_COLOR,
            font_size=18,
            anchor_x="center",
        )

        arcade.draw_text(
            "L — язык (RU/EN)\n"
            "1/2/3 — сложность\n"
            "M — режим (endless/timed)\n"
            "+ / - — время (если timed)\n"
            "ENTER / ESC — назад в меню",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT * 0.52,
            SUBTEXT_COLOR,
            font_size=18,
            anchor_x="center",
            multiline=True,
            width=820,
            align="center",
        )

        arcade.draw_text(
            f"Язык: {s.language.upper()}\n"
            f"Сложность: {s.difficulty}\n"
            f"Режим: {mode_name}\n"
            f"Время: {s.duration_sec} сек",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT * 0.30,
            TEXT_COLOR,
            font_size=22,
            anchor_x="center",
            multiline=True,
            width=820,
            align="center",
        )

    def on_key_press(self, symbol: int, modifiers: int):
        s = self.router.session.settings

        if symbol == arcade.key.L:
            s.language = "en" if s.language == "ru" else "ru"

        elif symbol == arcade.key.KEY_1:
            s.difficulty = 1
        elif symbol == arcade.key.KEY_2:
            s.difficulty = 2
        elif symbol == arcade.key.KEY_3:
            s.difficulty = 3

        elif symbol == arcade.key.M:
            s.mode = MODE_TIMED if s.mode == MODE_ENDLESS else MODE_ENDLESS

        elif symbol in (arcade.key.PLUS, arcade.key.EQUAL):
            s.duration_sec = min(600, s.duration_sec + 30)
        elif symbol == arcade.key.MINUS:
            s.duration_sec = max(60, s.duration_sec - 30)

        elif symbol in (arcade.key.ENTER, arcade.key.ESCAPE):
            from src.typing_fall.views_start_menu import MenuView
            self.router.go(MenuView(self.router))