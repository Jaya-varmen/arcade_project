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
from src.typing_fall.ui_models import Router


class ResultsView(arcade.View):
    """Финальное окно: результаты игры."""

    def __init__(self, router: Router, score: int, wpm: float, accuracy: float):
        super().__init__()
        self.router = router
        self.score = score
        self.wpm = wpm
        self.accuracy = accuracy

    def on_show_view(self):
        arcade.set_background_color(BG_COLOR)

    def on_draw(self):
        self.clear()

        arcade.draw_text(
            "Результаты",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT * 0.72,
            TEXT_COLOR,
            font_size=40,
            anchor_x="center",
        )

        arcade.draw_text(
            f"Игрок: {self.router.session.nickname}",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT * 0.62,
            ACCENT_COLOR,
            font_size=18,
            anchor_x="center",
        )

        arcade.draw_text(
            f"Очки: {self.score}\n"
            f"WPM: {self.wpm:.1f}\n"
            f"Accuracy: {self.accuracy*100:.1f}%",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT * 0.44,
            TEXT_COLOR,
            font_size=24,
            anchor_x="center",
            multiline=True,
            width=700,
            align="center",
        )

        arcade.draw_text(
            "ENTER — в меню\n3 — рейтинг",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT * 0.25,
            SUBTEXT_COLOR,
            font_size=18,
            anchor_x="center",
            multiline=True,
            width=700,
            align="center",
        )

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.KEY_3:
            self.router.go(LeaderboardView(self.router))
        elif symbol in (arcade.key.ENTER, arcade.key.ESCAPE):
            from src.typing_fall.views_start_menu import MenuView
            self.router.go(MenuView(self.router))


class LeaderboardView(arcade.View):
    """Экран рейтинга (TOP из SQLite)."""

    def __init__(self, router: Router):
        super().__init__()
        self.router = router
        self.rows: list[str] = []

    def on_show_view(self):
        arcade.set_background_color(BG_COLOR)

        from src.typing_fall.storage import Storage

        storage = Storage()
        top = storage.top_results(10)

        if not top:
            self.rows = ["Пока нет результатов. Сыграй первую игру :)"]
            return

        self.rows = []
        for i, r in enumerate(top, start=1):
            self.rows.append(f"{i}) {r.nickname} — {r.score} (WPM {r.wpm:.1f}, {r.accuracy*100:.0f}%)")

    def on_draw(self):
        self.clear()

        arcade.draw_text(
            "Рейтинг (TOP 10)",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT * 0.72,
            TEXT_COLOR,
            font_size=40,
            anchor_x="center",
        )

        y = SCREEN_HEIGHT * 0.60
        for line in self.rows[:10]:
            arcade.draw_text(
                line,
                SCREEN_WIDTH / 2,
                y,
                TEXT_COLOR,
                font_size=18,
                anchor_x="center",
            )
            y -= 30

        arcade.draw_text(
            "ENTER / ESC — в меню",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT * 0.18,
            SUBTEXT_COLOR,
            font_size=18,
            anchor_x="center",
        )

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol in (arcade.key.ENTER, arcade.key.ESCAPE):
            from src.typing_fall.views_start_menu import MenuView
            self.router.go(MenuView(self.router))