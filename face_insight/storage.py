from __future__ import annotations

import os
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path


def get_default_db_path() -> Path:
    """返回当前 Windows 用户自己的本地数据库路径。"""
    override = os.getenv("FACEINSIGHT_DATA_DIR")
    if override:
        return Path(override).expanduser().resolve() / "beauty_analysis.db"

    local_app_data = os.getenv("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data).resolve() / "FaceBeautyAnalysisSystem" / "beauty_analysis.db"
    return Path.home() / ".faceinsight" / "beauty_analysis.db"


DEFAULT_DB_PATH = get_default_db_path()


def remove_legacy_databases() -> list[Path]:
    """删除旧版本放在程序目录中的共享数据库，避免新用户看到旧记录。"""
    candidates = [Path.cwd() / "beauty_analysis.db"]
    if getattr(sys, "frozen", False):
        candidates.append(Path(sys.executable).resolve().parent / "beauty_analysis.db")

    removed: list[Path] = []
    for path in dict.fromkeys(candidate.resolve() for candidate in candidates):
        if path == DEFAULT_DB_PATH.resolve() or not path.exists():
            continue
        try:
            path.unlink()
            removed.append(path)
        except OSError:
            pass
    return removed


@dataclass(frozen=True)
class AnalysisRecord:
    record_id: int
    keyword: str
    score_counts: list[int]
    beauty_avg: float | None


def connect(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    if str(db_path) != ":memory:":
        Path(db_path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def create_table(conn: sqlite3.Connection) -> None:
    sql = """
    CREATE TABLE IF NOT EXISTS beauty_analysis(
        id             INTEGER PRIMARY KEY,
        keyword        TEXT NOT NULL,
        count_has_face INTEGER NOT NULL,
        count_no_face  INTEGER NOT NULL,
        num_one        INTEGER NOT NULL,
        num_two        INTEGER NOT NULL,
        num_three      INTEGER NOT NULL,
        num_four       INTEGER NOT NULL,
        num_five       INTEGER NOT NULL,
        num_six        INTEGER NOT NULL,
        num_seven      INTEGER NOT NULL,
        num_eight      INTEGER NOT NULL,
        num_nine       INTEGER NOT NULL,
        num_ten        INTEGER NOT NULL,
        beauty_avg     REAL
    );
    """
    conn.execute(sql)


def calculate_average(score_counts: list[int]) -> float | None:
    """有人脸数量为 0 时返回 None，修复课堂笔记里的除零 bug。"""
    face_count = sum(score_counts[1:])
    if face_count == 0:
        return None
    total = sum(score * count for score, count in enumerate(score_counts))
    return round(total / face_count, 2)


def save_analysis(
    conn: sqlite3.Connection,
    keyword: str,
    score_counts: list[int],
    beauty_avg: float | None,
) -> int:
    sql = """
    INSERT INTO beauty_analysis(
        keyword, count_has_face, count_no_face,
        num_one, num_two, num_three, num_four, num_five, num_six,
        num_seven, num_eight, num_nine, num_ten, beauty_avg
    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?);
    """
    params = (
        keyword,
        sum(score_counts[1:]),
        score_counts[0],
        *score_counts[1:],
        beauty_avg,
    )
    cursor = conn.execute(sql, params)
    conn.commit()
    return int(cursor.lastrowid)


def fetch_history(conn: sqlite3.Connection) -> list[AnalysisRecord]:
    cursor = conn.execute(
        """
        SELECT id, keyword, count_no_face,
               num_one, num_two, num_three, num_four, num_five, num_six,
               num_seven, num_eight, num_nine, num_ten, beauty_avg
        FROM beauty_analysis
        ORDER BY id;
        """
    )
    records: list[AnalysisRecord] = []
    for row in cursor.fetchall():
        score_counts = [row[2], *row[3:13]]
        records.append(AnalysisRecord(row[0], row[1], score_counts, row[13]))
    return records
