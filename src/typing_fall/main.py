import arcade

from src.typing_fall.constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_TITLE,
    BG_COLOR,
    TEXT_COLOR,
    SUBTEXT_COLOR,
    NICKNAME_MIN_LEN,
    NICKNAME_MAX_LEN,
)


class StartView(arcade.View):
    def __init__(self):
        super().__init__()
        self.nickname: str = ""
        self.message: str = "Введите ник и нажмите ENTER"

        # Используем arcade.Text вместо draw_text (меньше лагов/предупреждений)
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

        # поле ввода (рамка)
        left = SCREEN_WIDTH / 2 - 260
        right = SCREEN_WIDTH / 2 + 260
        bottom = SCREEN_HEIGHT * 0.48 - 30
        top = SCREEN_HEIGHT * 0.48 + 30
        arcade.draw_lrbt_rectangle_outline(
            left,
            right,
            bottom,
            top,
            SUBTEXT_COLOR,
            border_width=2,
        )

        # введённый ник
        shown = self.nickname if self.nickname else ""
        arcade.draw_text(
            shown,
            SCREEN_WIDTH / 2 - 240,
            SCREEN_HEIGHT * 0.48 - 12,
            TEXT_COLOR,
            font_size=24,
            anchor_x="left",
        )

        self.len_hint_text.draw()

        # сообщение
        self.message_text.text = self.message
        self.message_text.draw()

    def on_text(self, text: str):
        # Игнорируем пробелы/переводы строк
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

            self.message = f"Принято: {nick}. (Дальше будет меню)"
            arcade.close_window()


def main() -> None:
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.show_view(StartView())
    arcade.run()


if __name__ == "__main__":
    main()
