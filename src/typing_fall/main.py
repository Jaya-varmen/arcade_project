import arcade

from src.typing_fall.constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_TITLE,
    BG_COLOR,
    TEXT_COLOR,
    SUBTEXT_COLOR,
)


class StartView(arcade.View):
    def on_show_view(self):
        arcade.set_background_color(BG_COLOR)

    def on_draw(self):
        self.clear()

        arcade.draw_text(
            "Typing Fall",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 40,
            TEXT_COLOR,
            font_size=48,
            anchor_x="center",
        )
        arcade.draw_text(
            "Press ENTER to start (placeholder)",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 - 20,
            SUBTEXT_COLOR,
            font_size=20,
            anchor_x="center",
        )

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ENTER:
            arcade.close_window()


def main() -> None:
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.show_view(StartView())
    arcade.run()


if __name__ == "__main__":
    main()
