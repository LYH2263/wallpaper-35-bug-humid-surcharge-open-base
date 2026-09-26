import tempfile
from pathlib import Path

from app import config, seed
from app.repositories import history, settings_repo, walls
from app.services import estimate_service
import app.db as db


def setup_function(_):
    # 每个用例用全新临时库（config.DATA_DIR 在导入时已固化，需直接改 DB_PATH）
    tmp = Path(tempfile.mkdtemp(prefix="wp-test-svc-"))
    db_path = tmp / "app.db"
    config.DB_PATH = db_path
    db.DB_PATH = db_path
    seed.init_db()


def test_normal_wall_order_equals_base():
    out = estimate_service.run_estimate(1, 1, save=False, note="")
    assert out["space_type"] == "normal"
    assert out["order_rolls"] == out["rolls"]
    assert out["damp_rule_applied"] is False


def test_damp_wall_order_base_plus_extra():
    walls.set_space_type(1, "damp")
    out = estimate_service.run_estimate(1, 1, save=False, note="")
    assert out["space_type"] == "damp"
    assert out["damp_rule_applied"] is True
    assert out["order_rolls"] == out["rolls"] + 1  # 默认加 1 卷


def test_disabling_rule_returns_new_estimates_to_base():
    walls.set_space_type(1, "damp")
    assert estimate_service.run_estimate(1, 1, False, "")["order_rolls"] == 12  # 11+1
    settings_repo.update_settings({"damp_rule_enabled": False})
    out = estimate_service.run_estimate(1, 1, False, "")
    assert out["order_rolls"] == 11
    assert out["damp_rule_applied"] is False


def test_history_keeps_snapshot_when_settings_change_later():
    walls.set_space_type(1, "damp")
    saved = estimate_service.run_estimate(1, 1, save=True, note="写入时+1卷")
    assert saved["order_rolls"] == 12

    # 之后把加卷枚数改成 5：历史仍显示写入时的订货卷数与类型
    settings_repo.update_settings({"damp_extra_rolls": 5})
    runs = history.list_runs()
    assert len(runs) == 1
    r = runs[0]["result"]
    assert r["rolls"] == 11
    assert r["order_rolls"] == 12
    assert r["space_type"] == "damp"
    assert r["damp_extra_rolls"] == 1
    assert r["damp_rule_applied"] is True

    # 新测算才使用新加卷枚数
    new = estimate_service.run_estimate(1, 1, save=False, note="")
    assert new["order_rolls"] == 16  # 11+5


def test_history_stays_pinned_after_rule_disabled():
    walls.set_space_type(1, "damp")
    saved = estimate_service.run_estimate(1, 1, save=True, note="写入时启用+1")
    assert saved["order_rolls"] == 12

    # 随后停用规则：旧编号打开仍是写入时的类型与加损订货，不退回基础
    settings_repo.update_settings({"damp_rule_enabled": False})
    r = history.list_runs()[0]["result"]
    assert r["rolls"] == 11
    assert r["order_rolls"] == 12
    assert r["space_type"] == "damp"
    assert r["damp_rule_applied"] is True
    assert r["damp_extra_rolls"] == 1

    # 新测算（即使墙面仍潮湿）回到基础卷数
    new = estimate_service.run_estimate(1, 1, save=True, note="停用后新单")
    assert new["order_rolls"] == 11
    assert new["damp_rule_applied"] is False

    # 两笔同列：旧单钉住加损，新单为基础，互不串台
    rows = history.list_runs()
    by_note = {row["note"]: row["result"] for row in rows}
    assert by_note["写入时启用+1"]["order_rolls"] == 12
    assert by_note["停用后新单"]["order_rolls"] == 11


def test_legacy_run_without_snapshot_falls_back_to_base():
    # 模拟旧版本写入：result_json 里没有订货快照字段
    history.insert_run(1, 1, {"rolls": 11, "drops": 31}, note="旧单")
    r = history.list_runs()[0]["result"]
    assert r["order_rolls"] == 11
    assert r["space_type"] == "normal"
    assert r["damp_rule_applied"] is False
    assert r["damp_extra_rolls"] == 0


def test_history_filter_by_wall():
    estimate_service.run_estimate(1, 1, save=True, note="")
    estimate_service.run_estimate(2, 1, save=True, note="")
    only_w1 = history.list_runs(wall_id=1)
    assert {row["wall_id"] for row in only_w1} == {1}
