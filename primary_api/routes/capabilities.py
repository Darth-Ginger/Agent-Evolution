from fastapi import APIRouter, HTTPException
from typing import List
from prometheus_client import Counter

from ..db.NodeManager import NodeManager
from ..db.neo4j import get_neo4j_driver
from ..models.models import Capability, NodeUpdate

# Initialize the FastAPI router
router = APIRouter()

# Initialize the metrics
capability_creation_counter = Counter("capability_creation_count", "Number of capabilities")
capability_deletion_counter = Counter("capability_deletion_count", "Number of capabilities")

# Neo4j driver (replace with your driver instance)
driver = get_neo4j_driver()
# Instantiate the NodeManager
manager = NodeManager(driver)

# Create
@router.post("/", response_model=Capability)
async def create_capability(data: Capability) -> dict:
    result = manager.create_node("Capability", data)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to create capability")
    capability_creation_counter.inc()
    return {"Capability created successfully": data}

# Read
@router.get("/", response_model=List[Capability])
async def list_capabilities() -> List[Capability]:
    results = manager.get_nodes("Capability")
    return [Capability(**record["n"]) for record in results]

@router.get("/{id}", response_model=Capability)
async def get_capability(id: str) -> Capability:
    """
    Get a capability by ID.
    """
    result = manager.get_node("Capability", id)
    if not result:
        raise HTTPException(status_code=404, detail="Capability not found")
    return Capability(**result["n"])

# Update
@router.put("/{id}", response_model=Capability)
async def update_capability(id: str, update_data: NodeUpdate) -> dict:
    """
    Update an capability's properties based on the provided partial body.

    - **name**: Optional new name for the capability.
    - **base_prompt**: Optional new base prompt for the capability.
    - **operation**: Determines how to handle capabilities:
        - `overwrite`: Replace existing capabilities with the provided list.
        - `append`: Add the provided capabilities to the existing ones.
        - `remove`: Remove the provided capabilities from the existing ones.
    """
    capability = manager.update_node("Capability", id, update_data.updates, update_data.operation)
    if not capability:
        raise HTTPException(status_code=400, detail="Failed to update capability")
    return {"Capability updated successfully": capability}

# DELETE endpoint
@router.delete("/{id}")
async def delete_capability(id: str) -> dict:
    manager.delete_node("Capability", id)
    capability_deletion_counter.inc()
    return {"message": "Capability deleted"}
