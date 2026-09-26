import json
from datetime import datetime, timezone

from app.db import connect


def insert_run(wall_id: int, roll_id: int, result: dict, note: str = "") -> int:
    conn = connect()
    try:
        cur = conn.execute(
            "INSERT INTO calc_runs(wall_id,roll_id,result_json,note,created_at) VALUES (?,?,?,?,?)",
            (wall_id, roll_id, json.dumps(result, ensure_ascii=False), note, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def _legacy_result(result: dict) -> dict:
    """旧记录没有订货快照：订货卷数回退为当时的基础 rolls，类型按普通墙显示。"""
    result.setdefault("order_rolls", result.get("rolls"))
    result.setdefault("space_type", "normal")
    result.setdefault("damp_rule_applied", False)
    result.setdefault("damp_extra_rolls", 0)
    return result


def list_runs(limit: int = 50, wall_id: int | None = None):
    conn = connect()
    try:
        if wall_id is not None:
            rows = conn.execute(
                """
                SELECT r.*, w.name wall_name, rl.name roll_name
                FROM calc_runs r
                LEFT JOIN walls w ON w.id=r.wall_id
                LEFT JOIN rolls rl ON rl.id=r.roll_id
                WHERE r.wall_id=?
                ORDER BY r.id DESC LIMIT ?
                """,
                (wall_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT r.*, w.name wall_name, rl.name roll_name
                FROM calc_runs r
                LEFT JOIN walls w ON w.id=r.wall_id
                LEFT JOIN rolls rl ON rl.id=r.roll_id
                ORDER BY r.id DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
        out = []
        for row in rows:
            d = dict(row)
            # 历史只读：result_json 是写入时的快照，打开编号时不得按当前设置/规则重算
            d["result"] = _legacy_result(json.loads(d.pop("result_json")))
            out.append(d)
        return out
    finally:
        conn.close()
