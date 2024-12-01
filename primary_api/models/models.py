from pydantic import BaseModel
from typing import Literal, Optional

class CypherQuery(BaseModel):
    query: str
    parameters: dict = {}
      
class Relationship(BaseModel):
    start_node_label: str  # e.g., "Agent"
    start_node_id: str     # e.g., "agent1"
    end_node_label: str    # e.g., "Task"
    end_node_id: str       # e.g., "task1"
    relationship_type: str # e.g., "ASSIGNED_TO"
    
class Agent(BaseModel):
    id: str
    name: str
    capabilities: list[str] = []  # A list of capabilities the agent can perform
    base_prompt: str = "You are an agent"
    
class AgentUpdate(BaseModel):
    name: Optional[str] = None
    capabilities: Optional[list[str]] = None
    base_prompt: Optional[str] = None
    capabilities_operation: Optional[Literal["overwrite", "append", "remove"]] = "overwrite"
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Agent",
                "base_prompt": "You are an updated AI agent.",
                "capabilities": ["Coding", "Reviewing"],
                "capabilities_operation": "append",
            }
        }

class Task(BaseModel):
    id: str
    description: str
    status: str = "UNASSIGNED" # Default Status
    
class TaskUpdate(BaseModel):
    description: Optional[str] = None
    status: Optional[str] = None
    
    class Config:
        from_attributes = True
    
class Capability(BaseModel):
    id: str  # Unique identifier for the capability
    name: str  # Human-readable name for the capability