from __future__ import annotations

from dataclasses import dataclass, field
import arcade


MODE_ENDLESS = "endless"
MODE_TIMED = "timed"


@dataclass
class Settings:
    language: str = "ru"       # "ru" | "en"
    difficulty: int = 1        # 1..3
    mode: str = MODE_ENDLESS   # endless | timed
    duration_sec: int = 60     # 60..600


@dataclass
class Session:
    nickname: str = ""
    settings: Settings = field(default_factory=Settings)


class Router:
    """Переключение экранов внутри одного окна + общий Session."""

    def __init__(self, window: arcade.Window, session: Session):
        self.window = window
        self.session = session

    def go(self, view: arcade.View) -> None:
        self.window.show_view(view)
