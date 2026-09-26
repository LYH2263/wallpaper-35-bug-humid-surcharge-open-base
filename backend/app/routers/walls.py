from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.modules.damp_space import SpaceType
from app.repositories import walls as repo

router = APIRouter()


class SpaceTypeBody(BaseModel):
    space_type: str


@router.get("/walls")
def list_walls():
    return {"items": repo.list_walls()}


@router.get("/walls/{wall_id}")
def get_wall(wall_id: int):
    row = repo.get_wall(wall_id)
    if not row:
        raise HTTPException(404)
    return row


@router.patch("/walls/{wall_id}/space-type")
def update_space_type(wall_id: int, body: SpaceTypeBody):
    if body.space_type not in SpaceType.values():
        raise HTTPException(422, f"space_type 必须是 {SpaceType.values()} 之一")
    row = repo.set_space_type(wall_id, body.space_type)
    if not row:
        raise HTTPException(404)
    return row
