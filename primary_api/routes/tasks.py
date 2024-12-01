from fastapi import APIRouter, HTTPException
from typing import List
from ..models.models import Task, TaskUpdate
from ..db.neo4j import get_neo4j_driver, node_exists
from prometheus_client import Counter

# Initialize the APIRouter
router = APIRouter()
# Initialize the Prometheus Counters
task_creation_counter = Counter("task_creation_count", "Number of tasks")
task_deletion_counter = Counter("task_deletion_count", "Number of tasks")

# Initialize the tasks list
tasks: List[Task] = []

# Create
@router.post("/")
async def create_task(task: Task):
    if node_exists("Task", "id", task.id):
        raise HTTPException(status_code=400, detail="Task already exists")
    
    task_creation_counter.inc()
    driver = get_neo4j_driver()
    with driver.session() as session:
    # Create the task in Neo4j
        session.run(
            """
            CREATE (t:Task {id: $id, description: $description, status: $status})
            """,
            {"id": task.id, "description": task.description, "status": task.status}
        )
    return {"message": "Task created successfully", "task": task}

# Read
@router.get("/")
async def get_tasks():
    driver = get_neo4j_driver()
    with driver.session() as session:
        result = session.run("MATCH (t:Task) RETURN t.id AS id, t.description AS description, t.status AS status")
        tasks = [{"id": record["id"], "description": record["description"], "status": record["status"]} for record in result]
    return {"tasks": tasks}

@router.get("/{task_id}")
async def get_task(task_id: str):
    driver = get_neo4j_driver()
    with driver.session() as session:
        result = session.run("MATCH (t:Task {id: $id}) RETURN t", {"id": task_id})
        task = result.single()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found.")
    return {"task": {"id": task["t"]["id"], "description": task["t"]["description"], "status": task["t"]["status"]}}

# Update
@router.put("/{task_id}")
async def update_task(task_id: str, update: TaskUpdate):
    # Check if the task exists
    if node_exists("Task", "id", task_id):
        raise HTTPException(status_code=404, detail="Task not found.")
    
    driver = get_neo4j_driver()
    with driver.session() as session:
        
        # Build the Cypher SET statement dynamically based on provided fields
        updates = []
        parameters = {"id": task_id}
        if update.description is not None:
            updates.append("t.description = $description")
            parameters["description"] = update.description
        if update.status is not None:
            updates.append("t.status = $status")
            parameters["status"] = update.status
        
        if updates:
            # Update the task
            query = f"""
                     MATCH (t:Task {{id: $id}})
                     SET {', '.join(updates)}
                     """
            session.run(query, parameters)
            
    return {"message": "Task updated successfully"}

# Delete
@router.delete("/{task_id}")
async def delete_task(task_id: str):
    # Check if the task exists
    if not node_exists("Task", "id", task_id):
        raise HTTPException(status_code=404, detail="Task not found.")
    
    task_deletion_counter.inc()
    driver = get_neo4j_driver()
    with driver.session() as session:    
        # Delete the task
        session.run("MATCH (t:Task {id: $id}) DETACH DELETE t", {"id": task_id})
    return {"message": "Task deleted successfully"}
