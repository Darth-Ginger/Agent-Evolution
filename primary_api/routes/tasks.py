from fastapi import APIRouter, HTTPException
from typing import List
from prometheus_client import Counter

from ..db.NodeManager import NodeManager
from ..db.neo4j import get_neo4j_driver, node_exists
from ..models.models import Task, NodeUpdate

# Initialize the APIRouter
router = APIRouter()
# Initialize the Prometheus Counters
task_creation_counter = Counter("task_creation_count", "Number of tasks")
task_deletion_counter = Counter("task_deletion_count", "Number of tasks")

# Neo4j driver (replace with your driver instance)
driver = get_neo4j_driver()
# Instantiate the NodeManager
manager = NodeManager(driver)

# Initialize the tasks list
tasks: List[Task] = []

# Create
@router.post("/", response_model=Task)
async def create_task(task: Task) -> dict:
    result = manager.create_node("Task", task)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to create task")
    task_creation_counter.inc()
    return {"Task created successfully": task}

# Read
@router.get("/", response_model=List[Task])
async def get_tasks() -> List[Task]:
    tasks = manager.get_nodes("Task")
    return [Task(**task["n"]) for task in tasks]

@router.get("/{task_id}", response_model=Task)
async def get_task(task_id: str) -> Task:
    """
    Get a specific task by ID.
    """
    task = manager.get_node("Task", task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return Task(**task["n"])

# Update
@router.put("/{task_id}", response_model=Task)
async def update_task(task_id: str, update: NodeUpdate):
    """
    Update an capability's properties based on the provided partial body.

    - **name**: Optional new name for the capability.
    - **base_prompt**: Optional new base prompt for the capability.
    - **operation**: Determines how to handle capabilities:
        - `overwrite`: Replace existing capabilities with the provided list.
        - `append`: Add the provided capabilities to the existing ones.
        - `remove`: Remove the provided capabilities from the existing ones.
    """
    task = manager.update_node("Task", task_id, update.updates, update.operation)
    if not task:
        raise HTTPException(status_code=400, detail="Failed to update task")
    return {"Task updated successfully": task}

# Delete
@router.delete("/{task_id}")
async def delete_task(task_id: str):
    manager.delete_node("Task", task_id)
    task_deletion_counter.inc()
    return {"message": "Task deleted"}
