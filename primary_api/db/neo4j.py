from neo4j import GraphDatabase

def get_neo4j_driver():
    uri = "bolt://neo4j:7687"
    user = "neo4j"
    password = "password"
    return GraphDatabase.driver(uri, auth=(user, password))

def node_exists(label: str, property_name: str, property_value: str) -> bool:
    """
    Check if a node with a specific label and property exists in Neo4j.
    
    Args:
        label (str): The label of the node (e.g., "Task", "Agent").
        property_name (str): The property to match (e.g., "id").
        property_value (str): The value of the property to search for.
    
    Returns:
        bool: True if the node exists, False otherwise.
    """
    driver = get_neo4j_driver()
    query = f"MATCH (n:{label} {{{property_name}: $value}}) RETURN n"
    with driver.session() as session:
        result = session.run(query, {"value": property_value})
        return result.single() is not None
    
