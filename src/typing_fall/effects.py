from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import random
import arcade


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    radius: float
    color: tuple[int, int, int]


class Effects:
    """
    Эффекты проекта:
    - звуки (если файлы есть в assets/sounds)
    - частицы (простой particle system)
    """

    def __init__(self, sounds_dir: str = "assets/sounds"):
        self.sounds_dir = Path(sounds_dir)
        self.sounds: dict[str, arcade.Sound] = {}
        self.particles: list[Particle] = []

        # Не падаем, если файлов нет. Просто не загрузим звук.
        self._load_sound("correct", "correct.wav")
        self._load_sound("wrong", "wrong.wav")
        self._load_sound("miss", "miss.wav")
        self._load_sound("click", "click.wav")

    def _load_sound(self, key: str, filename: str) -> None:
        path = self.sounds_dir / filename
        if path.exists():
            self.sounds[key] = arcade.load_sound(str(path))

    def play(self, key: str, volume: float = 0.4) -> None:
        snd = self.sounds.get(key)
        if snd:
            arcade.play_sound(snd, volume=volume)

    def burst(
        self,
        x: float,
        y: float,
        color: tuple[int, int, int],
        n: int = 18,
        radius: float = 3.0,
    ) -> None:
        """Всплеск частиц (под успешный ввод или промах)."""
        for _ in range(n):
            vx = random.uniform(-160, 160)
            vy = random.uniform(80, 280)
            life = random.uniform(0.35, 0.7)
            r = random.uniform(max(1.5, radius - 1), radius + 2)
            self.particles.append(Particle(x, y, vx, vy, life, r, color))

    def update(self, dt: float) -> None:
        """Обновление физики частиц."""
        alive: list[Particle] = []
        for p in self.particles:
            p.life -= dt
            if p.life <= 0:
                continue

            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vy -= 520 * dt  # гравитация

            alive.append(p)

        self.particles = alive

    def draw(self) -> None:
        """Отрисовка частиц."""
        for p in self.particles:
            arcade.draw_circle_filled(p.x, p.y, p.radius, p.color)
