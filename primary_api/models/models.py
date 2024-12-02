from pydantic import BaseModel
from typing import Dict, Literal, Optional


class CypherQuery(BaseModel):
    query: str
    parameters: dict = {}
      
class Relationship(BaseModel):
    start_node_label: str  # e.g., "Agent"
    start_node_id: str     # e.g., "agent1"
    end_node_label: str    # e.g., "Task"
    end_node_id: str       # e.g., "task1"
    relationship_type: str # e.g., "ASSIGNED_TO"

class NodeBase(BaseModel):
    id: str
    description: Optional[str] = None

    class Config:
        from_attributes = True
        extra = 'allow'

class Agent(NodeBase):
    name: str
    capabilities: list[str] = []  # A list of capabilities the agent can perform
    base_prompt: str = "You are an agent"

class Task(NodeBase):
    status: str = "UNASSIGNED" # Default Status
    
class Capability(NodeBase):
    name: str

class NodeUpdate(BaseModel):
    updates: Dict[str, Optional[str]]
    operation: Literal["overwrite", "append", "remove"] = "overwrite"
