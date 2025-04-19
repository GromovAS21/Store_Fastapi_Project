from datetime import datetime, timezone, timedelta

from fastapi import APIRouter
from tasks import call_background_task

router = APIRouter(prefix="/tests", tags=["tests"])

@router.get("/hello")
async def hello(message: str):
    """
    Запланированная функция, которая выполняется в отдельном потоке в зависимости от очереди.
    """
    call_background_task.delay(message)
    return {'message': 'Hello World!'}

@router.get("/bye")
async def bye(message: str):
    """
    Запланированная Функция, которая выполняется в отдельном потоке с обратным отсчетом для выполнения.
    """
    call_background_task.apply_async(args=[message], countdown=60*5)
    return {'message': 'Bye World!'}

@router.get("/good")
async def good(message: str):
    """
    Запланированная Функция, которая выполняется в отдельном потоке к определенному времени.
    """
    task_datetime = datetime.now(timezone.utc) + timedelta(minutes=10)
    call_background_task.apply_async(args=[message], eta=task_datetime)
    return {'message': 'Hello World!'}