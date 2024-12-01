from fastapi import APIRouter
from typing import List
from app.models.task import Task

router = APIRouter()

tasks: List[Task] = []

@router.post("/tasks/")
async def create_task(task: Task):
    tasks.append(task)
    return {"status": "Task added", "task": task}

@router.get("/tasks/")
async def get_tasks():
    return {"tasks": tasks}
