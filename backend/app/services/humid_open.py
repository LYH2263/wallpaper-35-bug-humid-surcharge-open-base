"""Shape payloads for history open views (damp-space surcharge)."""

from __future__ import annotations

from copy import deepcopy


def has_humid_fields(result: dict) -> bool:
    return result.get("order_rolls") is not None or result.get("space_type") is not None


def base_rolls(result: dict) -> int | None:
    raw = result.get("rolls")
    if raw is None:
        return None
    return int(raw)


def open_drop_surcharge(result: dict) -> dict:
    """Keep space_type / damp flags, but set order_rolls back to base rolls."""
    if not isinstance(result, dict):
        return result
    out = deepcopy(result)
    if not has_humid_fields(out):
        return out
    base = base_rolls(out)
    if base is None:
        return out
    out["order_rolls"] = base
    out["open_surcharge_dropped"] = True
    # Flags stay so the UI can still show 潮湿 +N even when order equals base.
    out.setdefault("damp_rule_applied", bool(out.get("damp_rule_applied")))
    out.setdefault("damp_extra_rolls", int(out.get("damp_extra_rolls") or 0))
    return out


def summarize_humid(result: dict) -> dict:
    """Flat view of space type / surcharge / order for open consumers."""
    if not isinstance(result, dict):
        return {}
    return {
        "space_type": result.get("space_type"),
        "damp_rule_applied": bool(result.get("damp_rule_applied")),
        "damp_extra_rolls": result.get("damp_extra_rolls"),
        "rolls": result.get("rolls"),
        "order_rolls": result.get("order_rolls"),
        "open_surcharge_dropped": bool(result.get("open_surcharge_dropped")),
    }
