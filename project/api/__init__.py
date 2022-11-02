from fastapi import APIRouter

api_router = APIRouter(
    prefix="/api/v1",
)

from . import views, models, tasks, schemas  # noqa
