from fastapi import HTTPException

from app.engines.wallpaper_math import roll_count
from app.modules.damp_space import DampRule, SpaceType
from app.repositories import history, rolls, settings_repo, walls


def run_estimate(wall_id: int, roll_id: int, save: bool, note: str):
    wall = walls.get_wall(wall_id)
    if not wall:
        raise HTTPException(404, "wall not found")
    roll = rolls.get_roll(roll_id)
    if not roll:
        raise HTTPException(404, "roll not found")
    if wall.get("data_quality") == "dirty" or roll.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty seed entity")

    space_type = SpaceType.normalize(wall.get("space_type"))

    # 基础卷数：对花/条带纯数学测算
    calc = roll_count(
        wall["perimeter"], wall["height"], roll["width"], roll["length"], roll["pattern_cm"]
    )

    # 订货卷数：在基础 rolls 上按潮湿空间规则加固定卷数（规则可在设置页停用）
    enabled, extra = settings_repo.get_damp_rule()
    rule = DampRule(enabled, extra)
    order_rolls = rule.order_rolls(calc["rolls"], space_type)
    rule_info = rule.describe(space_type)

    result = {
        **calc,
        "wall_id": wall_id,
        "roll_id": roll_id,
        # rolls 保持为基础卷数；订货卷数与类型单独快照，历史不被后来改设置带跑
        "order_rolls": order_rolls,
        **rule_info,
    }

    run_id = None
    if save:
        run_id = history.insert_run(wall_id, roll_id, result, note)
    return {"wall": wall, "roll": roll, "run_id": run_id, **result}
