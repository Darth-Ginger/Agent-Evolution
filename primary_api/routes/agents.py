from fastapi import APIRouter, HTTPException
from prometheus_client import Counter
from ..models.models import Agent, AgentUpdate
from ..db.neo4j import get_neo4j_driver, node_exists

# Initialize the APIRouter
router = APIRouter()

# Initialize the Prometheus Counters
agent_creation_counter = Counter("agent_creation_count", "Number of agents")
agent_deletion_counter = Counter("agent_deletion_count", "Number of agents")

# Create
@router.post("/")
async def create_agent(agent: Agent):
    """
    Create an agent in Neo4j.
    """
    driver = get_neo4j_driver()
    with driver.session() as session:
        # Check if the agent already exists
        if node_exists("Agent", "id", agent.id):
            raise HTTPException(status_code=400, detail="Agent already exists.")

        agent_creation_counter.inc()
        # Create the agent node
        session.run(
            """
            CREATE (a:Agent {id: $id, name: $name, base_prompt: $base_prompt})
            """,
            {"id": agent.id, "name": agent.name, "base_prompt": agent.base_prompt}
        )

        # Add capabilities as relationships
        for capability_name in agent.capabilities:
            capability_id = capability_name.replace(" ", "_")
            session.run(
                """
                MERGE (c:Capability {id: $capability_id, name: $capability_name})
                MATCH (a:Agent {id: $id})
                MERGE (a)-[:CAN_EXECUTE]->(c)
                """,
                {"capability_id": capability_id, "capability_name": capability_name, "id": agent.id}
            )
    return {"message": "Agent created successfully"}

# Read
@router.get("/")
async def get_agents():
    """
    List all agents.
    """
    driver = get_neo4j_driver()
    with driver.session() as session:
        result = session.run("MATCH (a:Agent) RETURN a.id AS id, a.name AS name")
        agents = [{"id": record["id"], "name": record["name"]} for record in result]
    return {"agents": agents}

@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    """
    Get an agent by ID.
    """
    driver = get_neo4j_driver()
    with driver.session() as session:
        result = session.run("MATCH (a:Agent {id: $id}) RETURN a.id AS id, a.name AS name", {"id": agent_id})
        agent = result.single()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found.")
        return {"id": agent["id"], "name": agent["name"]}

# Update
@router.put("/{agent_id}", 
            summary="Update an agent", 
            description="Update agent details, including name, base_prompt, \
                            and capabilities. Supports operations to overwrite, \
                            append, or remove capabilities.")
async def update_agent(agent_id: str, update: AgentUpdate):
    """
    Update an agent's properties based on the provided partial body.

    - **name**: Optional new name for the agent.
    - **base_prompt**: Optional new base prompt for the agent.
    - **capabilities**: List of capabilities to modify.
    - **capabilities_operation**: Determines how to handle capabilities:
        - `overwrite`: Replace existing capabilities with the provided list.
        - `append`: Add the provided capabilities to the existing ones.
        - `remove`: Remove the provided capabilities from the existing ones.
    """
    driver = get_neo4j_driver()
    with driver.session() as session:
        # Check if the agent exists
        agent = session.run("MATCH (a:Agent {id: $id}) RETURN a", {"id": agent_id}).single()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found.")
        
        # Build the Cypher SET statement dynamically based on provided fields
        updates = []
        parameters = {"id": agent_id}
        if update.name is not None:
            updates.append("a.name = $name")
            parameters["name"] = update.name
        if update.base_prompt is not None:
            updates.append("a.base_prompt = $base_prompt")
            parameters["base_prompt"] = update.base_prompt

        # Handle capabilities based on the operation type
        if update.capabilities is not None:
            if update.capabilities_operation == "overwrite":
                # Remove existing capabilities and replace with the new list
                session.run(
                    """
                    MATCH (a:Agent {id: $id})-[r:CAN_EXECUTE]->()
                    DELETE r
                    """,
                    {"id": agent_id}
                )
                for capability_name in update.capabilities:
                    capability_id = capability_name.replace(" ", "_")
                    session.run(
                        """
                        MERGE (c:Capability {id: $capability_id, name: $capability_name})
                        MATCH (a:Agent {id: $id})
                        MERGE (a)-[:CAN_EXECUTE]->(c)
                        """,
                        {"capability_id": capability_id, "capability_name": capability_name, "id": agent_id}
                    )

            elif update.capabilities_operation == "append":
                # Add the new capabilities without removing existing ones
                for capability_name in update.capabilities:
                    capability_id = capability_name.replace(" ", "_")
                    session.run(
                        """
                        MERGE (c:Capability {id: $capability_id, name: $capability_name})
                        MATCH (a:Agent {id: $id})
                        MERGE (a)-[:CAN_EXECUTE]->(c)
                        """,
                        {"capability_id": capability_id, "capability_name": capability_name, "id": agent_id}
                    )

            elif update.capabilities_operation == "remove":
                # Remove the specified capabilities
                for capability_name in update.capabilities:
                    capability_id = capability_name.replace(" ", "_")
                    session.run(
                        """
                        MATCH (a:Agent {id: $id})-[r:CAN_EXECUTE]->(c:Capability {id: $capability_id})
                        DELETE r
                        """,
                        {"id": agent_id, "capability_id": capability_id}
                    )

        # Execute updates for name and base_prompt
        if updates:
            query = f"""
                MATCH (a:Agent {{id: $id}})
                SET {', '.join(updates)}
            """
            session.run(query, parameters)

    return {"message": "Agent updated successfully"}

# Delete
@router.delete("/{agent_id}")
async def delete_agent(agent_id: str):
    # Check if the agent exists
    if not node_exists("Agent", "id", agent_id):
        raise HTTPException(status_code=404, detail="Agent not found.")
    
    agent_deletion_counter.inc()
    driver = get_neo4j_driver()
    with driver.session() as session:
        # Delete the agent
        session.run("MATCH (a:Agent {id: $id}) DETACH DELETE a", {"id": agent_id})
    return {"message": "Agent deleted successfully"}