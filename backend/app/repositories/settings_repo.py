from app.db import connect
from app.modules.damp_space import SpaceType

DAMP_ENABLED_KEY = "damp_rule_enabled"
DAMP_EXTRA_KEY = "damp_extra_rolls"


def get_all() -> dict:
    conn = connect()
    try:
        return {r["key"]: r["value"] for r in conn.execute("SELECT key,value FROM settings").fetchall()}
    finally:
        conn.close()


def _is_enabled(v) -> bool:
    return str(v).strip().lower() in ("1", "true", "yes", "on")


def get_damp_rule() -> tuple[bool, int]:
    """返回 (是否启用潮湿加损规则, 固定加卷枚数)。"""
    all_settings = get_all()
    enabled = _is_enabled(all_settings.get(DAMP_ENABLED_KEY, "1"))
    try:
        extra = int(all_settings.get(DAMP_EXTRA_KEY, "1"))
    except (TypeError, ValueError):
        extra = 1
    return enabled, max(0, extra)


def update_settings(updates: dict) -> dict:
    """只允许写 settings 表自身的键值，绝不触碰历史表 calc_runs。

    返回规范化后的潮湿规则设置 (enabled, extra_rolls, space_type 枚举不由这里管)。
    """
    allowed = {DAMP_ENABLED_KEY, DAMP_EXTRA_KEY, "unit"}
    sets: dict[str, str] = {}
    if DAMP_ENABLED_KEY in updates:
        sets[DAMP_ENABLED_KEY] = "1" if bool(updates[DAMP_ENABLED_KEY]) else "0"
    if DAMP_EXTRA_KEY in updates:
        try:
            extra = int(updates[DAMP_EXTRA_KEY])
        except (TypeError, ValueError):
            raise ValueError("damp_extra_rolls 必须是非负整数")
        if extra < 0:
            raise ValueError("damp_extra_rolls 必须是非负整数")
        sets[DAMP_EXTRA_KEY] = str(extra)
    if "unit" in updates and updates["unit"] is not None:
        sets["unit"] = str(updates["unit"])

    unknown = set(updates) - allowed
    if unknown:
        raise ValueError(f"未知设置项: {sorted(unknown)}")

    if sets:
        conn = connect()
        try:
            conn.executemany(
                "INSERT INTO settings(key,value) VALUES (?,?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                list(sets.items()),
            )
            conn.commit()
        finally:
            conn.close()

    enabled, extra = get_damp_rule()
    return {
        DAMP_ENABLED_KEY: enabled,
        DAMP_EXTRA_KEY: extra,
        "space_types": SpaceType.values(),
    }
