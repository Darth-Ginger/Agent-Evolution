from fastapi import APIRouter, HTTPException
from typing import List
from prometheus_client import Counter

from ..db.NodeManager import NodeManager
from ..db.neo4j import get_neo4j_driver
from ..models.models import Agent, NodeUpdate

# Initialize the APIRouter
router = APIRouter()

# Initialize the Prometheus Counters
agent_creation_counter = Counter("agent_creation_count", "Number of agents")
agent_deletion_counter = Counter("agent_deletion_count", "Number of agents")

# Neo4j driver (replace with your driver instance)
driver = get_neo4j_driver()
# Instantiate the NodeManager
manager = NodeManager(driver)

# Create
@router.post("/", response_model=Agent)
async def create_agent(data: Agent):
    """
    Create a new agent.
    """
    result = manager.create_node("Agent", data)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to create agent")
    # Add capabilities as relationships
    for capability_name in data.capabilities:
        capability_id = capability_name.replace(" ", "_")
        manager.create_relationship("Agent", data.id, "Capability", capability_id, capability_name)
    return {"Agent created successfully": data}

# Read
@router.get("/", response_model=List[Agent])
async def get_agents() -> List[Agent]:
    """
    Get all agents.
    """
    agents = manager.get_nodes("Agent")
    return [Agent(**agent["n"]) for agent in agents]

@router.get("/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str) -> Agent:
    """
    Get an agent by ID.
    """
    agent = manager.get_node("Agent", agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found.")
    return Agent(**agent["n"])

# Update
@router.put("/{agent_id}", response_model=Agent)
async def update_agent(agent_id: str, update: NodeUpdate) -> dict:
    """
    Update an agent's properties based on the provided partial body.

    - **name**: Optional new name for the agent.
    - **base_prompt**: Optional new base prompt for the agent.
    - **capabilities**: List of capabilities to modify.
    - **operation**: Determines how to handle capabilities:
        - `overwrite`: Replace existing capabilities with the provided list.
        - `append`: Add the provided capabilities to the existing ones.
        - `remove`: Remove the provided capabilities from the existing ones.
    """
    agent = manager.update_node("Agent", agent_id, update.updates, update.operation)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found.")
    return {"Agent updated successfully": agent}

# Delete
@router.delete("/{agent_id}")
async def delete_agent(agent_id: str) -> dict:
    manager.delete_node("Agent", agent_id)
    return {"message": "Agent deleted"}