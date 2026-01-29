from __future__ import annotations

from pathlib import Path
import random


class WordProvider:
    """
    Загружает слова из assets/words/{lang}_{difficulty}.txt
    Пример: ru_1.txt, en_3.txt
    """

    def __init__(self, words_dir: str = "assets/words"):
        self.words_dir = Path(words_dir)
        self._cache: dict[tuple[str, int], list[str]] = {}

    def _read_file(self, path: Path) -> list[str]:
        if not path.exists():
            return []
        words: list[str] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            w = line.strip()
            if w:
                words.append(w)
        return words

    def get_word(self, language: str, difficulty: int) -> str:
        key = (language, int(difficulty))
        if key not in self._cache:
            filename = f"{language}_{difficulty}.txt"
            words = self._read_file(self.words_dir / filename)

            # чтобы игра никогда не падала
            if not words:
                words = ["test", "word", "typing"] if language == "en" else ["тест", "слово", "печать"]

            self._cache[key] = words

        return random.choice(self._cache[key])