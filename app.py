from typing import Union
import random

from fastapi import FastAPI

from functions import images

from functions import neo4jRequests

from rdflib import Graph

app = FastAPI()

g = Graph()
g.parse("inferenceDef.rdf")

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
                RETURN courseTaken.ns0__name as name, courseTaken.ns0__language as language, courseTaken.ns0__description as description, courseTaken.uri as uri, SIZE(COLLECT(user)) AS userCount
                ORDER BY userCount DESC LIMIT 10;'''
    result = neo4jRequests.execute_query(query)
    for d in result:
        del d["userCount"]
        name =d["name"]
        d["urlImage"] = images.get_image_by_keyword(name)
    return {"courses":result}

@app.get("/courses_by_related_term/{username}")
def courses_by_related_term(username:str):
    query = f'''MATCH (user)-[:ns0__tookCourse]->(courses)
                MATCH (courses)-[:ns0__hasKeyTerm]->(keyterm)
                MATCH (relatedCourse)-[:ns0__hasKeyTerm]->(keyterm)
                WHERE (user.ns0__personName = "{username}") and NOT (user)-[:ns0__tookCourse]->(relatedCourse)
                RETURN DISTINCT relatedCourse.ns0__name as name, relatedCourse.ns0__language as language, relatedCourse.ns0__description as description, relatedCourse.uri as uri, keyterm.ns0__hasTerm as KeyTerm'''
    result = random.sample(neo4jRequests.execute_query(query),10)
    # for i in result:
    #     name =i["name"]
    #     i["urlImage"] = images.get_image_by_keyword(name)
    return {"courses":result}

@app.get("/favorite-category/{username}")
def favorite_category(username:str):
    query = f'''MATCH (user)-[:ns0__tookCourse]->(courseTaken)
                MATCH (courseTaken)-[:ns0__courseHas]->(category)
                WHERE user.ns0__personName = "{username}"
                RETURN category.ns0__name AS name,SIZE(COLLECT(courseTaken)) AS courseCount
                ORDER BY courseCount DESC
                LIMIT 10;'''
    result = neo4jRequests.execute_query(query)
    cati = result[:10]
    lista = [];
    for cat in cati:
        query2 = f'''
            MATCH (category)-[:ns0__hasCourse]->(relatedCourse)
            WHERE category.ns0__name = "{cat["name"]}"
            RETURN  relatedCourse.ns0_name as name, relatedCourse.ns0language as language, relatedCourse.ns0_description as description, relatedCourse.uri as uri
        '''
        exc = neo4jRequests.execute_query(query2)
        if len(exc)>=10:
            result2 = random.sample(exc,10)
        else:
            result2 = exc
        print(cat)
        cat["urlImage"] = images.get_image_by_keyword(cat["name"]);
        cat["courses"] = result2
        lista.append(cat)
    return {"categories":lista}



@app.get("/courses_by_language/{username}")
def course_by_language(username:str):
    query = f'''
                MATCH (user)-[:ns0__tookCourse]->(course)
                MATCH (otherCourse:ns0__Course)
                WHERE course.ns0__language = otherCourse.ns0__language AND NOT (user)-[:ns0__tookCourse]->(otherCourse) AND user.ns0__personName = "{username}"
                RETURN otherCourse.ns0__name as name, otherCourse.ns0__language as language, otherCourse.ns0__description as description, otherCourse.uri as uri;'''
    result = random.sample(neo4jRequests.execute_query(query),10)
    # for i in result:
    #     name =i["name"]
    #     i["urlImage"] = images.get_image_by_keyword("test")
    return {"courses":result}

@app.get("/courses_partners/{username}")
def courses_partners(username:str):
    query = f'''
                MATCH (user)-[:ns0__tookCourse]->(course)
                MATCH (otherUser)-[:ns0__tookCourse]->(course)
                MATCH (otherUser)-[:ns0__tookCourse]->(otherCourse)
                WHERE user.ns0__personName = "{username}" AND otherUser <> user AND NOT (user)-[:ns0__tookCourse]->(otherCourse)
                RETURN DISTINCT otherCourse.ns0__name as name, otherCourse.ns0__language as language, otherCourse.ns0__description as description, otherCourse.uri as uri;
    '''
    result = random.sample(neo4jRequests.execute_query(query),10)
    # for i in result:
    #     name =i["name"]
    #     i["urlImage"] = images.get_image_by_keyword("test")
    return {"courses":result}


@app.get("/detail_course/{course}")
def detail_course(course:str):
    queryGetBasicInfo = f'''
    PREFIX uexvocab: <http://www.uniandes.web.semantica.ejemplo.org/voca#>
    SELECT DISTINCT ?course ?name ?language ?description ?link
    WHERE{{
    ?course uexvocab:name ?name.
    ?course uexvocab:language ?language.
    ?course uexvocab:description ?description.
    ?course uexvocab:link ?link.
    FILTER(STR(?name) = "{course}")
    }}
    LIMIT 1
    '''
 
    result = g.query(queryGetBasicInfo)
    basic = {}
    for res in result:
        basic = {"name":str(res["name"]), "uri":str(res["course"]), "language":str(res["language"]), "description":str(res["description"]), "link":str(res["link"])}

    getCategory = f'''
    PREFIX uexvocab: <http://www.uniandes.web.semantica.ejemplo.org/voca#>
    SELECT DISTINCT ?category ?name ?link
    WHERE{{
    ?category uexvocab:hasCourse ?course.
    ?course uexvocab:name ?nameCourse.
    OPTIONAL{{?category uexvocab:link ?link}}
    ?category uexvocab:name ?name.
    FILTER(STR(?nameCourse) = "{course}")
    }}
    LIMIT 1
    '''
    
    result = g.query(getCategory)
    cat = {}
    for re in result:
        cat["name"] = str(re["name"])
        cat["link"] = str(re["link"])
        cat["uri"] = str(re["category"])
    
    getLessons = f'''
    PREFIX uexvocab: <http://www.uniandes.web.semantica.ejemplo.org/voca#>
    SELECT DISTINCT ?lesson ?name ?content
    WHERE {{
    ?course uexvocab:hasLesson ?lesson.
    ?lesson uexvocab:name ?name.
    ?course uexvocab:name ?cuName.
    OPTIONAL{{ ?lesson uexvocab:hasContent ?content}}
    FILTER(str(?cuName) = "{course}")
    }}
    '''
    result = g.query(getLessons)
    lesson = []

    for re in result:
        le = {"name":str(re["name"]), "content":re["content"], "uri":re["lesson"]}
        lesson.append(le)

    getKeys = f'''
    PREFIX uexvocab: <http://www.uniandes.web.semantica.ejemplo.org/voca#>
    SELECT DISTINCT ?keyTerm ?term (GROUP_CONCAT(?link; separator=",") AS ?links)
    WHERE {{
    ?course uexvocab:hasKeyTerm ?keyTerm.
    ?keyTerm uexvocab:hasTerm ?term.
    ?course uexvocab:name ?cuName.
    ?keyTerm uexvocab:dbpediaLink ?link.
    FILTER(str(?cuName) = "{course}")
    }}
    GROUP BY ?keyTerm ?term
    '''
    result = g.query(getKeys)
    key = []

    for re in result:
        ke = {"term":str(re["term"]), "link":re["links"].split(","), "uri":re["keyTerm"]}
        key.append(ke)


    return {"course":{"basic":basic, "category":cat, "lessons":lesson, "keyTerms":key}}
