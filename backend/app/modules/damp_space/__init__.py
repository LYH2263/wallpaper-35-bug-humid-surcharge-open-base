"""潮湿空间加损模块：空间类型枚举与加损规则（枚举、规则、测算服务各自分文件）。"""

from app.modules.damp_space.rule import DampRule
from app.modules.damp_space.types import SpaceType

__all__ = ["SpaceType", "DampRule"]
