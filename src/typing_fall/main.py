import arcade

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SCREEN_TITLE = "Typing Fall (v0)"


class StartView(arcade.View):
    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "Typing Fall",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 40,
            arcade.color.WHITE,
            font_size=48,
            anchor_x="center",
        )
        arcade.draw_text(
            "Press ENTER to start (placeholder)",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 - 20,
            arcade.color.LIGHT_GRAY,
            font_size=20,
            anchor_x="center",
        )

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ENTER:
            # пока просто закрываем окно (дальше заменим на меню)
            arcade.close_window()


def main() -> None:
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.show_view(StartView())
    arcade.run()


if __name__ == "__main__":
    main()
