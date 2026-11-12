"""Read-only multi-factor directional strategy assessments."""
from fastapi import APIRouter, Response

from ..services.strategy_evaluation import evaluate_live

router = APIRouter(prefix="/strategies", tags=["Strategy evaluation"])


@router.get("/evaluate")
def evaluate(response: Response):
    response.headers["Cache-Control"] = "no-store"
    return evaluate_live()
