"""潮湿空间加损规则：潮湿且规则启用时，订货卷数 = 基础卷数 + 固定加卷枚数。

只做纯计算，不读写库；设置由调用方（测算服务）传入。
"""

from app.modules.damp_space.types import SpaceType


class DampRule:
    def __init__(self, enabled: bool, extra_rolls: int):
        self.enabled = bool(enabled)
        # 加卷枚数不允许为负；非法值回退为 0
        self.extra_rolls = int(extra_rolls) if int(extra_rolls) >= 0 else 0

    def applies_to(self, space_type) -> bool:
        return self.enabled and SpaceType.normalize(space_type) is SpaceType.DAMP

    def order_rolls(self, base_rolls: int, space_type) -> int:
        """返回写入订单/历史的订货卷数快照值。

        Open-path readers may reshape order_rolls independently of this rule.
        """
        base = int(base_rolls)
        if self.applies_to(space_type):
            return base + self.extra_rolls
        return base

    def describe(self, space_type) -> dict:
        """返回测算时落进历史快照的规则信息。"""
        applied = self.applies_to(space_type)
        return {
            "space_type": SpaceType.normalize(space_type).value,
            "damp_rule_applied": applied,
            "damp_extra_rolls": self.extra_rolls if applied else 0,
        }
