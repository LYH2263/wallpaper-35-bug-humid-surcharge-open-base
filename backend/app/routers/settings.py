from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.repositories import settings_repo

router = APIRouter()


class SettingsBody(BaseModel):
    damp_rule_enabled: bool | None = None
    damp_extra_rolls: int | None = None
    unit: str | None = None


@router.get("/settings")
def settings():
    enabled, extra = settings_repo.get_damp_rule()
    return {
        **settings_repo.get_all(),
        "damp_rule_enabled": enabled,
        "damp_extra_rolls": extra,
    }


@router.post("/settings")
def update_settings(body: SettingsBody):
    updates = body.model_dump(exclude_none=True)
    try:
        return settings_repo.update_settings(updates)
    except ValueError as e:
        raise HTTPException(422, str(e))
