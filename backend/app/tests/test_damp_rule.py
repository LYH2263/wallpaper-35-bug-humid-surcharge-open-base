from app.modules.damp_space import DampRule, SpaceType


def test_normal_wall_equals_base_even_when_rule_enabled():
    rule = DampRule(enabled=True, extra_rolls=2)
    assert rule.order_rolls(11, SpaceType.NORMAL) == 11
    info = rule.describe(SpaceType.NORMAL)
    assert info["space_type"] == "normal"
    assert info["damp_rule_applied"] is False
    assert info["damp_extra_rolls"] == 0


def test_damp_wall_adds_fixed_extra_when_enabled():
    rule = DampRule(enabled=True, extra_rolls=2)
    assert rule.order_rolls(11, SpaceType.DAMP) == 13
    info = rule.describe(SpaceType.DAMP)
    assert info["space_type"] == "damp"
    assert info["damp_rule_applied"] is True
    assert info["damp_extra_rolls"] == 2


def test_damp_wall_falls_back_to_base_when_disabled():
    rule = DampRule(enabled=False, extra_rolls=2)
    assert rule.order_rolls(11, SpaceType.DAMP) == 11
    info = rule.describe(SpaceType.DAMP)
    assert info["damp_rule_applied"] is False
    assert info["damp_extra_rolls"] == 0


def test_extra_zero_means_equal_base_for_damp():
    assert DampRule(True, 0).order_rolls(5, SpaceType.DAMP) == 5


def test_unknown_type_normalized_to_normal():
    assert SpaceType.normalize("weird") is SpaceType.NORMAL
    assert DampRule(True, 3).order_rolls(7, "weird") == 7
