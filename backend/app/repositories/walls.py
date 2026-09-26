from app.db import connect
from app.modules.damp_space import SpaceType


def list_walls():
    conn = connect()
    try:
        return [dict(r) for r in conn.execute("SELECT * FROM walls ORDER BY id").fetchall()]
    finally:
        conn.close()


def get_wall(wid: int):
    conn = connect()
    try:
        row = conn.execute("SELECT * FROM walls WHERE id=?", (wid,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def set_space_type(wid: int, space_type: str):
    t = SpaceType.normalize(space_type)
    conn = connect()
    try:
        cur = conn.execute("UPDATE walls SET space_type=? WHERE id=?", (t.value, wid))
        conn.commit()
        if cur.rowcount == 0:
            return None
    finally:
        conn.close()
    return get_wall(wid)
