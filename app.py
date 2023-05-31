from typing import Union
import random

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
    query = '''MATCH (user) -[:ns0__tookCourse]->(courseTaken)
                RETURN courseTaken.ns0__name, SIZE(COLLECT(user)) AS userCount
                ORDER BY userCount DESC LIMIT 10;'''
    result = neo4jRequests.execute_query(query)
    return result

@app.get("/courses_by_related_term")
def courses_by_related_term():
    query = '''MATCH (user)-[:ns0__tookCourse]->(courses)
                MATCH (courses)-[:ns0__hasKeyTerm]->(keyterm)
                MATCH (relatedCourse)-[:ns0__hasKeyTerm]->(keyterm)
                WHERE (user.ns0__personName = "Philip_Vega_Sánchez") and NOT (user)-[:ns0__tookCourse]->(relatedCourse)
                RETURN DISTINCT relatedCourse, keyterm  LIMIT 10'''
    result = neo4jRequests.execute_query(query)
    return result

@app.get("/favorite-category")
def favorite_category():
    query = '''MATCH (user)-[:ns0__tookCourse]->(courseTaken)
                MATCH (courseTaken)-[:ns0__courseHas]->(category)
                WHERE user.ns0__personName = "Carolina_Clark_Clark"
                RETURN category.ns0__name ,SIZE(COLLECT(courseTaken)) AS courseCount
                ORDER BY courseCount DESC
                LIMIT 10;'''
    result = neo4jRequests.execute_query(query)
    return result


@app.get("/courses_by_language")
def course_by_language():
    query = '''
                MATCH (user)-[:ns0__tookCourse]->(course)
                MATCH (otherCourse:ns0__Course)
                WHERE course.ns0__language = otherCourse.ns0__language AND NOT (user)-[:ns0__tookCourse]->(otherCourse) AND user.ns0__personName = "Carolina_Clark_Clark"
                RETURN otherCourse.ns0__name as name, otherCourse.ns0__language as language, otherCourse.ns0__description as description, otherCourse.uri as uri;'''
    result = random.sample(neo4jRequests.execute_query(query),10)
    for i in result:
        name =i["name"]
        i["urlImage"] = images.get_image_by_keyword(name)
    return {"courses":result}