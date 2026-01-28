from __future__ import annotations

import arcade

from src.typing_fall.constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    BG_COLOR,
    TEXT_COLOR,
    SUBTEXT_COLOR,
    ACCENT_COLOR,
    NICKNAME_MIN_LEN,
    NICKNAME_MAX_LEN,
)
from src.typing_fall.ui_models import Router


class StartView(arcade.View):
    """Стартовое окно: ввод ника."""

    def __init__(self, router: Router):
        super().__init__()
        self.router = router
        self.nickname = router.session.nickname
        self.message = "Введите ник и нажмите ENTER"

        self.title_text = arcade.Text(
            "Typing Fall",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT * 0.70,
            TEXT_COLOR,
            font_size=48,
            anchor_x="center",
        )
        self.len_hint_text = arcade.Text(
            f"Длина ника: {NICKNAME_MIN_LEN}-{NICKNAME_MAX_LEN}",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT * 0.38,
            SUBTEXT_COLOR,
            font_size=18,
            anchor_x="center",
        )
        self.message_text = arcade.Text(
            self.message,
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT * 0.28,
            SUBTEXT_COLOR,
            font_size=18,
            anchor_x="center",
        )

    def on_show_view(self):
        arcade.set_background_color(BG_COLOR)

    def on_draw(self):
        self.clear()
        self.title_text.draw()

        # рамка поля ввода
        left = SCREEN_WIDTH / 2 - 260
        right = SCREEN_WIDTH / 2 + 260
        bottom = SCREEN_HEIGHT * 0.48 - 30
        top = SCREEN_HEIGHT * 0.48 + 30
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, SUBTEXT_COLOR, border_width=2)

        # введённый ник
        arcade.draw_text(
            self.nickname,
            SCREEN_WIDTH / 2 - 240,
            SCREEN_HEIGHT * 0.48 - 12,
            TEXT_COLOR,
            font_size=24,
            anchor_x="left",
        )

        self.len_hint_text.draw()
        self.message_text.text = self.message
        self.message_text.draw()

    def on_text(self, text: str):
        if text.strip() == "":
            return
        if len(self.nickname) >= NICKNAME_MAX_LEN:
            return
        self.nickname += text
        self.message = "Введите ник и нажмите ENTER"

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.BACKSPACE:
            self.nickname = self.nickname[:-1]
            self.message = "Введите ник и нажмите ENTER"
            return

        if symbol == arcade.key.ENTER:
            nick = self.nickname.strip()
            if len(nick) < NICKNAME_MIN_LEN:
                self.message = f"Ник слишком короткий (мин. {NICKNAME_MIN_LEN})"
                return

            self.router.session.nickname = nick
            self.router.go(MenuView(self.router))


class MenuView(arcade.View):
    """Главное меню (пока заглушки пунктов)."""

    def __init__(self, router: Router):
        super().__init__()
        self.router = router

        self.title_text = arcade.Text(
            "Главное меню",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT * 0.70,
            TEXT_COLOR,
            font_size=42,
            anchor_x="center",
        )
        self.hint_text = arcade.Text(
            "1 — Настройки (скоро)\n2 — Старт игры (скоро)\n3 — Рейтинг (скоро)\nESC — Выход",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT * 0.45,
            SUBTEXT_COLOR,
            font_size=20,
            anchor_x="center",
            multiline=True,
            width=760,
            align="center",
        )

    def on_show_view(self):
        arcade.set_background_color(BG_COLOR)

    def on_draw(self):
        self.clear()
        self.title_text.draw()

        arcade.draw_text(
            f"Игрок: {self.router.session.nickname}",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT * 0.58,
            ACCENT_COLOR,
            font_size=18,
            anchor_x="center",
        )

        self.hint_text.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            arcade.close_window()