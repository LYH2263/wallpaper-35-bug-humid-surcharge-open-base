"""墙面空间类型枚举。"""

from enum import Enum


class SpaceType(str, Enum):
    NORMAL = "normal"
    DAMP = "damp"

    @classmethod
    def values(cls) -> list[str]:
        return [t.value for t in cls]

    @classmethod
    def normalize(cls, value) -> "SpaceType":
        """把库中/请求里的值规范成枚举，未知值按普通墙处理。"""
        if isinstance(value, SpaceType):
            return value
        try:
            return cls(str(value))
        except ValueError:
            return cls.NORMAL
