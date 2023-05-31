from neo4j import GraphDatabase

# Establecer la conexión
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "neo4j"))

def execute_query(cypher_query):
    with driver.session() as session:
        result = session.run(cypher_query)
        return result.data()
    