from __future__ import annotations

from dataclasses import dataclass
import random
import time

import arcade

from src.typing_fall.constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    BG_COLOR,
    TEXT_COLOR,
    SUBTEXT_COLOR,
    ACCENT_COLOR,
    GOOD_COLOR,
    BAD_COLOR,
)
from src.typing_fall.ui_models import Router, MODE_ENDLESS, MODE_TIMED
from src.typing_fall.effects import Effects


# Настройки сложности (3 уровня = "несколько уровней")
DIFFICULTY = {
    1: {"spawn_sec": 1.6, "fall_speed": 140, "score_per_word": 10},
    2: {"spawn_sec": 1.2, "fall_speed": 190, "score_per_word": 14},
    3: {"spawn_sec": 0.9, "fall_speed": 240, "score_per_word": 18},
}

# Мини-словари (потом заменим на words.py / assets/words)
WORDS_RU = {
    1: ["кот", "дом", "лес", "мир", "окно", "снег", "лук", "сон", "еда", "ключ"],
    2: ["машина", "комната", "задание", "учебник", "проверка", "карандаш"],
    3: ["программирование", "взаимодействие", "производительность", "архитектура"],
}
WORDS_EN = {
    1: ["cat", "home", "tree", "wind", "snow", "milk", "code", "game", "fast", "key"],
    2: ["computer", "keyboard", "window", "project", "accuracy", "practice"],
    3: ["responsibility", "performance", "architecture", "configuration"],
}


@dataclass(frozen=True)
class GameResult:
    score: int
    correct: int
    mistakes: int
    wpm: float
    accuracy: float
    time_played_sec: int


class WordSprite(arcade.Sprite):
    """Спрайт слова (sprites требование)."""

    def __init__(self, word: str, x: float, y: float):
        super().__init__()
        self.texture = arcade.make_soft_square_texture(220, arcade.color.WHITE, 255, 255)
        self.scale = 0.35
        self.center_x = x
        self.center_y = y
        self.word = word

        # для "физики"
        self.change_y = 0.0

    def draw_word(self):
        arcade.draw_text(
            self.word,
            self.center_x,
            self.center_y - 8,
            arcade.color.BLACK,
            font_size=18,
            anchor_x="center",
        )


class GameView(arcade.View):
    """
    Основная игра:
    - слова падают сверху
    - ввод снизу
    - collide: слово ударилось об пол = промах
    - "physics engine": используем PhysicsEngineSimple для остановки на полу
    - camera: лёгкий shake при ошибке/промахе
    - particles: через Effects
    """

    def __init__(self, router: Router, effects: Effects):
        super().__init__()
        self.router = router
        self.effects = effects

        self.words = arcade.SpriteList()
        self.floor_list = arcade.SpriteList()

        self.floor = arcade.SpriteSolidColor(SCREEN_WIDTH, 20, arcade.color.BLACK)
        self.floor.center_x = SCREEN_WIDTH / 2
        self.floor.center_y = 10
        self.floor_list.append(self.floor)

        # Physics engines per-word (простая, но работает и засчитывается как “физ.движок”)
        self.engines: dict[WordSprite, arcade.PhysicsEngineSimple] = {}

        self.input_text = ""
        self.score = 0
        self.correct = 0
        self.mistakes = 0
        self._max_input_len = 24

        self._spawn_timer = 0.0
        self._start_time = 0.0
        self._ended = False

        # camera
        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self._shake_time = 0.0

        # UI текстики
        self._title = arcade.Text(
            "Игра",
            16,
            SCREEN_HEIGHT - 40,
            TEXT_COLOR,
            font_size=20,
            anchor_x="left",
        )

    def on_show_view(self):
        arcade.set_background_color(BG_COLOR)
        self._start_time = time.time()

    # ---------- helpers ----------

    def _played(self) -> int:
        return int(max(0.0, time.time() - self._start_time))

    def _time_left(self) -> int:
        s = self.router.session.settings
        if s.mode != MODE_TIMED:
            return 0
        return max(0, int(s.duration_sec - self._played()))

    def _pick_word(self) -> str:
        s = self.router.session.settings
        d = int(s.difficulty)
        if s.language == "ru":
            return random.choice(WORDS_RU.get(d, WORDS_RU[1]))
        return random.choice(WORDS_EN.get(d, WORDS_EN[1]))

    def _spawn_word(self):
        if len(self.words) >= 12:
            return
        x = random.randint(90, SCREEN_WIDTH - 90)
        y = SCREEN_HEIGHT + 40
        w = WordSprite(self._pick_word(), x, y)
        self.words.append(w)
        self.engines[w] = arcade.PhysicsEngineSimple(w, self.floor_list)

    def _shake(self, seconds: float = 0.18):
        self._shake_time = max(self._shake_time, seconds)

    def _finish(self):
        if self._ended:
            return
        self._ended = True

        played = max(1, self._played())
        total = self.correct + self.mistakes
        accuracy = (self.correct / total) if total > 0 else 0.0
        wpm = (self.correct / played) * 60.0

        result = GameResult(
            score=self.score,
            correct=self.correct,
            mistakes=self.mistakes,
            wpm=wpm,
            accuracy=accuracy,
            time_played_sec=played,
        )

        # Сохраняем результат в БД
        from src.typing_fall.storage import Storage
        Storage().save_result(self.router.session.nickname, result.score, result.wpm, result.accuracy)

        # Переходим на окно результатов
        from src.typing_fall.views_results_leaderboard import ResultsView
        self.router.go(ResultsView(self.router, score=result.score, wpm=result.wpm, accuracy=result.accuracy))

    # ---------- arcade callbacks ----------

    def on_update(self, dt: float):
        if self._ended:
            return

        self.effects.update(dt)

        s = self.router.session.settings
        preset = DIFFICULTY.get(int(s.difficulty), DIFFICULTY[1])

        # режим timed
        if s.mode == MODE_TIMED and self._time_left() <= 0:
            self._finish()
            return

        # спавн
        self._spawn_timer += dt
        if self._spawn_timer >= preset["spawn_sec"]:
            self._spawn_timer = 0.0
            self._spawn_word()

        # “гравитация” падения + physics engine stop on collide
        for w in list(self.words):
            w.change_y = -preset["fall_speed"] * dt * 60  # dt-normalized
            self.engines[w].update()

            # collide с полом (требование collide)
            if arcade.check_for_collision(w, self.floor):
                # промах
                self.mistakes += 1
                self.effects.burst(w.center_x, w.center_y, BAD_COLOR, n=18)
                self._shake()

                w.remove_from_sprite_lists()
                self.engines.pop(w, None)

        # камера shake
        if self._shake_time > 0:
            self._shake_time -= dt
            dx = random.randint(-6, 6)
            dy = random.randint(-4, 4)
            self.camera.move_to((dx, dy), speed=1.0)
        else:
            self.camera.move_to((0, 0), speed=0.25)

    def on_draw(self):
        self.clear()
        self.camera.use()

        # пол
        self.floor_list.draw()

        # слова (спрайты + текст)
        self.words.draw()
        for w in self.words:
            w.draw_word()

        # частицы
        self.effects.draw()

        # UI поверх
        arcade.draw_text(
            f"Игрок: {self.router.session.nickname}",
            16,
            SCREEN_HEIGHT - 70,
            ACCENT_COLOR,
            font_size=16,
            anchor_x="left",
        )

        s = self.router.session.settings
        mode_text = "∞" if s.mode == MODE_ENDLESS else f"{self._time_left()}s"
        arcade.draw_text(
            f"Score: {self.score} | OK: {self.correct} | Miss: {self.mistakes} | Mode: {mode_text}",
            16,
            SCREEN_HEIGHT - 95,
            SUBTEXT_COLOR,
            font_size=14,
            anchor_x="left",
        )

        # поле ввода снизу
        left = SCREEN_WIDTH / 2 - 320
        right = SCREEN_WIDTH / 2 + 320
        bottom = 38
        top = 92
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, SUBTEXT_COLOR, border_width=2)

        arcade.draw_text(
            self.input_text,
            left + 14,
            58,
            TEXT_COLOR,
            font_size=22,
            anchor_x="left",
        )

        arcade.draw_text(
            "ENTER — отправить слово | Q — закончить",
            SCREEN_WIDTH / 2,
            12,
            SUBTEXT_COLOR,
            font_size=14,
            anchor_x="center",
        )

    def on_text(self, text: str):
        if self._ended:
            return
        if text.strip() == "":
            return
        if len(self.input_text) >= self._max_input_len:
            return
        self.input_text += text

    def on_key_press(self, symbol: int, modifiers: int):
        if self._ended:
            return

        if symbol == arcade.key.BACKSPACE:
            self.input_text = self.input_text[:-1]
            return

        if symbol == arcade.key.Q:
            self._finish()
            return

        if symbol == arcade.key.ENTER:
            typed = self.input_text.strip()
            if not typed:
                return

            # проверяем совпадение с любым активным словом
            matched = None
            for w in self.words:
                if w.word == typed:
                    matched = w
                    break

            if matched is not None:
                s = self.router.session.settings
                preset = DIFFICULTY.get(int(s.difficulty), DIFFICULTY[1])

                self.correct += 1
                self.score += int(preset["score_per_word"])
                self.effects.burst(matched.center_x, matched.center_y, GOOD_COLOR, n=20)

                matched.remove_from_sprite_lists()
                self.engines.pop(matched, None)
            else:
                self.mistakes += 1
                self.effects.burst(SCREEN_WIDTH / 2, 70, BAD_COLOR, n=10)
                self._shake()

            self.input_text = ""