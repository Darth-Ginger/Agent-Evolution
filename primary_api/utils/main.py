from fastapi import FastAPI
from app.routes import tasks, neo4j

app = FastAPI()

# Include Modular Routes
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(neo4j.router, prefix="/neo4j", tags=["Neo4j"])


@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}
