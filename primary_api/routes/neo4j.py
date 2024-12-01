from fastapi import APIRouter, HTTPException
from ..db.neo4j import get_neo4j_driver
from ..models.models import CypherQuery, Relationship

router = APIRouter()

#region Metadata
@router.get("/stats")
async def get_database_stats():
    """
    Retrieve basic statistics about the Neo4j database.
    """
    driver = get_neo4j_driver()
    with driver.session() as session:
        node_count = session.run("MATCH (n) RETURN COUNT(n) AS count").single()["count"]
        relationship_count = session.run("MATCH ()-[r]->() RETURN COUNT(r) AS count").single()["count"]
    return {
        "node_count": node_count,
        "relationship_count": relationship_count
    }
    
@router.get("/health")
async def health_check():
    """
    Check the health of the Neo4j database connection.
    """
    driver = get_neo4j_driver()
    try:
        with driver.session() as session:
            session.run("RETURN 1")
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

#endregion

@router.post("/query")
async def run_custom_query(query: CypherQuery):
    """
    Execute a custom Cypher query against the Neo4j database.
    """
    driver = get_neo4j_driver()
    try:
        with driver.session() as session:
            result = session.run(query.query, query.parameters)
            # Return the query results as a list of dictionaries
            records = [record.data() for record in result]
        return {"result": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Query failed: {str(e)}")

@router.post("/relationships")
async def create_relationship(relationship: Relationship):
    """
    Create a relationship between two nodes in Neo4j.
    """
    driver = get_neo4j_driver()
    with driver.session() as session:
        # Validate that both nodes exist
        start_node_exists = session.run(
            f"MATCH (n:{relationship.start_node_label} {{id: $id}}) RETURN n",
            {"id": relationship.start_node_id}
        ).single()
        end_node_exists = session.run(
            f"MATCH (n:{relationship.end_node_label} {{id: $id}}) RETURN n",
            {"id": relationship.end_node_id}
        ).single()

        if not start_node_exists or not end_node_exists:
            raise HTTPException(
                status_code=404,
                detail="Start or end node not found in the database."
            )

        # Create the relationship
        session.run(
            f"""
            MATCH (a:{relationship.start_node_label} {{id: $start_id}})
            MATCH (b:{relationship.end_node_label} {{id: $end_id}})
            MERGE (a)-[r:{relationship.relationship_type}]->(b)
            """,
            {
                "start_id": relationship.start_node_id,
                "end_id": relationship.end_node_id,
            }
        )
    return {"message": "Relationship created successfully"}

@router.get("/relationships/{node_label}/{node_id}")
async def get_relationships(node_label: str, node_id: str):
    """
    Retrieve all relationships for a given node.
    """
    driver = get_neo4j_driver()
    with driver.session() as session:
        result = session.run(
            f"""
            MATCH (n:{node_label} {{id: $id}})-[r]->(m)
            RETURN type(r) AS relationship_type, labels(m) AS end_node_labels, m.id AS end_node_id
            """,
            {"id": node_id}
        )
        relationships = [
            {
                "relationship_type": record["relationship_type"],
                "end_node_labels": record["end_node_labels"],
                "end_node_id": record["end_node_id"],
            }
            for record in result
        ]
    return {"relationships": relationships}