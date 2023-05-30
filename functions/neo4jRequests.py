from neo4j import GraphDatabase

# Establecer la conexión
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "neo4j"))

def execute_query(cypher_query):
    with driver.session() as session:
        result = session.run(cypher_query)
        return result.data()
    
consulta = '''MATCH (user)-[:tookCourse]->(course)
                WITH course.name AS courseName, COUNT(user) AS userCount
                RETURN courseName, userCount
                ORDER BY userCount DESC
                LIMIT 10'''
resultado = execute_query(consulta)
for i in resultado:
    print("------------")
    print(i)