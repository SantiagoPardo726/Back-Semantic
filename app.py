from typing import Union

from fastapi import FastAPI

from functions import images

from functions import neo4jRequests

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/images/{key_word}")
def read_root(key_word:str):
    url_image = images.get_image_by_keyword(keyword=key_word)
    return {'url_image':url_image}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str|None = None):
    return {"item_id": item_id, "q": q}

@app.get("/get-top-10-courses")
def top_10_courses():
    query = '''MATCH (user)-[:tookCourse]->(course)
                WITH course.name AS courseName, COUNT(user) AS userCount
                RETURN courseName, userCount
                ORDER BY userCount DESC
                LIMIT 10'''
    result = neo4jRequests.execute_query(query)
    return result

