from fastapi import APIRouter, Query

from app.repositories import history as repo

router = APIRouter()


@router.get("/runs")
def list_runs(limit: int = 50, wall_id: int | None = Query(default=None)):
    return {"items": repo.list_runs(limit, wall_id=wall_id)}
