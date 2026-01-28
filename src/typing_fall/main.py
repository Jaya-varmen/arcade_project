import arcade

from src.typing_fall.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE
from src.typing_fall.ui_models import Session, Router
from src.typing_fall.views_start_menu import StartView


def main() -> None:
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

    session = Session()
    router = Router(window, session)

    router.go(StartView(router))
    arcade.run()


if __name__ == "__main__":
    main()