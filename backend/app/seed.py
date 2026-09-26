from app.db import connect
from app.modules.damp_space import SpaceType

DEFAULT_SETTINGS = {
    "unit": "roll",
    "damp_rule_enabled": "1",
    "damp_extra_rolls": "1",
}


def _has_column(conn, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r["name"] == column for r in rows)


def init_db():
    conn = connect()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS walls(
            id INTEGER PRIMARY KEY, name TEXT, perimeter REAL, height REAL,
            data_quality TEXT DEFAULT 'clean', note TEXT DEFAULT '',
            space_type TEXT DEFAULT 'normal'
        );
        CREATE TABLE IF NOT EXISTS rolls(
            id INTEGER PRIMARY KEY, name TEXT, width REAL, length REAL, pattern_cm REAL,
            data_quality TEXT DEFAULT 'clean', note TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE IF NOT EXISTS calc_runs(
            id INTEGER PRIMARY KEY AUTOINCREMENT, wall_id INTEGER, roll_id INTEGER,
            result_json TEXT, note TEXT, created_at TEXT
        );
        """
    )
    # 旧库迁移：为已有 walls 表补 space_type 列
    if not _has_column(conn, "walls", "space_type"):
        conn.execute(
            f"ALTER TABLE walls ADD COLUMN space_type TEXT DEFAULT '{SpaceType.NORMAL.value}'"
        )
    conn.execute(
        f"UPDATE walls SET space_type=? WHERE space_type IS NULL OR space_type NOT IN ({','.join('?' * len(SpaceType))})",
        [SpaceType.NORMAL.value, *SpaceType.values()],
    )

    for key, value in DEFAULT_SETTINGS.items():
        conn.execute("INSERT OR IGNORE INTO settings(key,value) VALUES (?,?)", (key, value))

    if conn.execute("SELECT COUNT(*) c FROM walls").fetchone()["c"] == 0:
        conn.executemany(
            "INSERT INTO walls(name,perimeter,height,data_quality,note,space_type) VALUES (?,?,?,?,?,?)",
            [
                ("主卧一圈", 16.0, 2.7, "clean", "", SpaceType.NORMAL.value),
                ("大花匹配", 20.0, 2.8, "clean", "需对花", SpaceType.NORMAL.value),
                ("主卫潮墙", 12.0, 2.6, "clean", "卫浴潮湿空间", SpaceType.DAMP.value),
                ("脏数据-零周长", 0.0, 2.7, "dirty", "周长为0", SpaceType.NORMAL.value),
            ],
        )
        conn.executemany(
            "INSERT INTO rolls(name,width,length,pattern_cm,data_quality,note) VALUES (?,?,?,?,?,?)",
            [
                ("素色53", 0.53, 10.0, 0, "clean", ""),
                ("大花64", 0.53, 10.0, 64, "clean", ""),
                ("脏数据-零宽", 0.0, 10.0, 0, "dirty", ""),
            ],
        )
    conn.commit()
    conn.close()
