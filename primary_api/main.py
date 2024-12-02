from fastapi import FastAPI
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from .routes import tasks, neo4j, agents, capabilities

DEBUG: bool = True

app = FastAPI(title="Primary API", 
              version="0.1.0",
              openapi_tags=[
                  {"name": "Tasks"},
                  {"name": "Neo4j"},
                  {"name": "Agents"},
                  {"name": "Capabilities"}
              ],
              openapi_url="/openapi.json",
              servers=[{"url": "http://10.20.0.40:8100"}],
              debug=DEBUG)

# Register Prometheus Instrumentator
Instrumentator().instrument(app).expose(app)

# Include Modular Routes
app.include_router(tasks.router       , prefix="/tasks"       , tags=["Tasks"])
app.include_router(neo4j.router       , prefix="/neo4j"       , tags=["Neo4j"])
app.include_router(agents.router      , prefix="/agents"      , tags=["Agents"])
app.include_router(capabilities.router, prefix="/capabilities", tags=["Capabilities"])

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

@app.get("/openapi", include_in_schema=False)
async def download_openapi():
    """
    Download the OpenAPI specification.
    """
    
    return JSONResponse(app.openapi())
