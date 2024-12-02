from enum import Enum
import re
from pydantic import BaseModel, Field, model_validator
from typing import Dict, Literal, Optional

from ..db.neo4j import get_neo4j_driver
from ..db.NodeManager import NodeManager

Manager = NodeManager(get_neo4j_driver())

class CypherQuery(BaseModel):
    query: str
    parameters: Dict[str, Optional[str]] = {}
      
class Relationship(BaseModel):
    start_node_label: str  # e.g., "Agent"
    start_node_id: str     # e.g., "agent1"
    end_node_label: str    # e.g., "Task"
    end_node_id: str       # e.g., "task1"
    relationship_type: str # e.g., "ASSIGNED_TO"
    created_at: Optional[str] = None  # ISO 8601 timestamp

class NodeBase(BaseModel):
    name: str = Field(default_factory=str, description="Human readable name for Node")
    id: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True
        extra = 'allow'
        
    @model_validator(mode="before")
    @classmethod
    def generate_id(cls, values):
        if not values.get('id'):
            # Generate ID by converting name
            base_id = re.sub(r"\s+", "_", values["name"].lower())
            values["id"] = base_id
            
            existing_ids = cls.check_existing_ids(base_id)
            if existing_ids:
                count = len(existing_ids) + 1
                values["id"] = f"{base_id}_{count}"
                
        return values
            
            
    @staticmethod
    def check_existing_ids(base_id) -> list[str]:
        existing_ids = []
        for node in Manager.get_like_nodes("id", base_id):
            if node["n"]["id"] == base_id:
                existing_ids.append(node["n"]["id"])
        return existing_ids

class Agent(NodeBase):
    capabilities: list[str] = []  # A list of capabilities the agent can perform
    base_prompt: str = "You are an agent"

class TaskStatus(str, Enum):
    UNASSIGNED  = "UNASSIGNED" # Default Status
    ASSIGNED    = "ASSIGNED"   # Task is assigned to an agent, but not yet started
    IN_PROGRESS = "IN_PROGRESS"# Task is in progress
    COMPLETED   = "COMPLETED"  # Task is completed

class Task(NodeBase):
    status: TaskStatus = TaskStatus.UNASSIGNED # Default Status
    asignee: Optional[Agent] = None
    
class Capability(NodeBase):
    valid_relationships: list[str] = Field(default_factory=list, description="List of valid relationships for this capability", examples=["ASSIGNED_TO", "CAN_EXECUTE", "USES"])

class NodeUpdate(BaseModel):
    updates: Dict[str, Optional[str]] = Field(default=None, description="Dictionary of updates to apply to the node", examples={"name": "New Name", "description": "New Description"})
    operation: Literal["overwrite", "append", "remove"] = "overwrite"
