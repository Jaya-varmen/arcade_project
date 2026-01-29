from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ResultRow:
    nickname: str
    score: int
    wpm: float
    accuracy: float
    created_at: str


class Storage:
    def __init__(self, db_path: str = "typing_fall.db"):
        self.db_path = Path(db_path)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS players(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nickname TEXT NOT NULL UNIQUE
                );
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS results(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    score INTEGER NOT NULL,
                    wpm REAL NOT NULL,
                    accuracy REAL NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    FOREIGN KEY(player_id) REFERENCES players(id)
                );
                """
            )

    def get_or_create_player_id(self, nickname: str) -> int:
        nickname = nickname.strip()
        with self._connect() as conn:
            cur = conn.execute("SELECT id FROM players WHERE nickname = ?;", (nickname,))
            row = cur.fetchone()
            if row:
                return int(row[0])

            conn.execute("INSERT INTO players(nickname) VALUES (?);", (nickname,))
            cur2 = conn.execute("SELECT id FROM players WHERE nickname = ?;", (nickname,))
            return int(cur2.fetchone()[0])

    def save_result(self, nickname: str, score: int, wpm: float, accuracy: float) -> None:
        self.init_schema()
        player_id = self.get_or_create_player_id(nickname)

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO results(player_id, score, wpm, accuracy)
                VALUES (?, ?, ?, ?);
                """,
                (player_id, int(score), float(wpm), float(accuracy)),
            )

    def top_results(self, limit: int = 10) -> list[ResultRow]:
        self.init_schema()

        with self._connect() as conn:
            cur = conn.execute(
                """
                SELECT p.nickname, r.score, r.wpm, r.accuracy, r.created_at
                FROM results r
                JOIN players p ON p.id = r.player_id
                ORDER BY r.score DESC, r.created_at DESC
                LIMIT ?;
                """,
                (int(limit),),
            )

            out: list[ResultRow] = []
            for nickname, score, wpm, accuracy, created_at in cur.fetchall():
                out.append(
                    ResultRow(
                        nickname=str(nickname),
                        score=int(score),
                        wpm=float(wpm),
                        accuracy=float(accuracy),
                        created_at=str(created_at),
                    )
                )
            return out