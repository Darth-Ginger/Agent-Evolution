from typing import Dict

from ..models.models import NodeBase
from .neo4j import get_neo4j_driver, node_exists

class NodeManager:
    def __init__(self, driver):
        self.driver = driver

    def create_node(self, node_type: str, data: NodeBase) -> dict: 
        with self.driver.session() as session:
            query = f"""
            CREATE (n:{node_type} {{ id: $id, {', '.join([f"{key}: ${key}" for key in data.dict().keys() if key != 'id'])} }})
            RETURN n
            """
            return session.run(query, **data.dict()).single()

    def update_node(self, node_type: str, node_id: str, updates: Dict, operation: str = "overwrite") -> dict:
        with self.driver.session() as session:
            if operation == "overwrite":
                # Overwrite specified properties
                update_string = ', '.join([f"{key}: ${key}" for key in updates.keys()])
                query = f"""
                MATCH (n:{node_type} {{ id: $id }})
                SET n += {{ {update_string} }}
                RETURN n
                """
                return session.run(query, id=node_id, **updates).single()
            
            elif operation == "remove":
                # Remove (unset) specified properties
                remove_string = ', '.join([f"n.{key} = null" for key in updates.keys()])
                query = f"""
                MATCH (n:{node_type} {{ id: $id }})
                SET {remove_string}
                RETURN n
                """
                return session.run(query, id=node_id).single()

            elif operation == "append":
                # Overwrite existing properties and add new properties
                append_string = ', '.join([f"n.{key} = $value_{key}" for key in updates.keys()])
                query = f"""
                MATCH (n:{node_type} {{ id: $id }})
                SET {append_string}
                RETURN n
                """
                params = {f"value_{key}": value for key, value in updates.items()}
                params["id"] = node_id
                return session.run(query, **params).single()

    def delete_node(self, node_type: str, node_id: str) -> None:
        query = f"""
        MATCH (n:{node_type} {{ id: $id }})
        DETACH DELETE n
        """
        with self.driver.session() as session:
            session.run(query, id=node_id)

    def create_relationship( self, 
            start_node_label: str = "Task", start_node_id: str = "", 
            end_node_label: str = "Agent", end_node_id: str = "", 
            relationship_type: str = "ASSIGNED_TO" ) -> None:

        query = f"""
        MATCH (start:{start_node_label} {{id: $start_id}}), (end:{end_node_label} {{id: $end_id}})
        CREATE (start)-[:{relationship_type}]->(end)
        """
        with self.driver.session() as session:
            session.run(query, start_id=start_node_id, end_id=end_node_id)
            
    def get_node(self, node_type: str, node_id: str) -> NodeBase:
        with self.driver.session() as session:
            result = session.run(f"MATCH (n:{node_type} {{id: $id}}) RETURN n", id=node_id).single()
        return NodeBase(**result["n"])
    
    def get_nodes(self, node_type: str) -> list[NodeBase]:
        with self.driver.session() as session:
            results = session.run(f"MATCH (n:{node_type}) RETURN n").data()
        return [NodeBase(**record["n"]) for record in results]
    
    def get_nodes(self, node_type: str, property_name: str, property_value: str) -> list[NodeBase]:
        with self.driver.session() as session:
            results = session.run(f"MATCH (n:{node_type} {{ {property_name}: $property_value }}) RETURN n", property_value=property_value).data()
        return [NodeBase(**record["n"]) for record in results]
    
    def get_nodes(self, property_name: str, property_value: str) -> list[NodeBase]:
        with self.driver.session() as session:
            results = session.run(f"MATCH (n {{ {property_name}: $property_value }}) RETURN n", property_value=property_value).data()
        return [NodeBase(**record["n"]) for record in results]
    
    def get_like_nodes(self, node_type: str, property_name: str, property_value: str) -> list[NodeBase]:
        with self.driver.session() as session:
            results = session.run(
                f"""
                MATCH (n:{node_type})
                WHERE n.{property_name} CONTAINS $property_value
                RETURN n
                """, 
                property_value=property_value
            ).data()
        return [NodeBase(**record["n"]) for record in results]
    
    def get_like_nodes(self, property_name: str, property_value: str) -> list[NodeBase]:
        with self.driver.session() as session:
            results = session.run(
                f"""
                MATCH (n)
                WHERE n.{property_name} CONTAINS $property_value
                RETURN n
                """, 
                property_value=property_value
            ).data()
        return [NodeBase(**record["n"]) for record in results]
    
    def node_exists(self, node_type: str, property_name: str, property_value: str) -> bool:
        return node_exists(node_type, property_name, property_value)
    
    def node_exists(self, property_name: str, property_value: str) -> bool:
        return node_exists(property_name, property_value)