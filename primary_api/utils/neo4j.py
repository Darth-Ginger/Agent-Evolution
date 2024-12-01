from fastapi import APIRouter
from ..db.neo4j import get_neo4j_driver

router = APIRouter()

@router.get("/neo4j/")
async def test_neo4j():
    driver = get_neo4j_driver()
    with driver.session() as session:
        result = session.run("MATCH (n) RETURN COUNT(n) AS count")
        count = result.single()["count"]
    return {"node_count": count}
