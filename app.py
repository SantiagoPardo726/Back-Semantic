from typing import Union
import random

from fastapi import FastAPI

from functions import images

from functions import neo4jRequests

from rdflib import Graph, Literal, Namespace, RDF
from fastapi.middleware.cors import CORSMiddleware

import pyshacl

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

g = Graph()
g.parse("InferenceDef.rdf")
UEX = Namespace("http://www.uniandes.web.semantica.example.org/")
UEXVOCAV = Namespace("http://www.uniandes.web.semantica.ejemplo.org/voca#")

s = Graph()
s.parse("ShapeCourse.rdf", format="turtle")

ng = Graph()
ng.parse("justClassCat.rdf")


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
            RETURN  relatedCourse.ns0__name as name, relatedCourse.ns0__language as language, relatedCourse.ns0__description as description, relatedCourse.uri as uri
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
    image = images.get_image_by_keyword(course);
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
        le = {"name":str(re["name"]), "content":str(re["content"]), "uri":str(re["lesson"])}
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
        ke = {"term":str(re["term"]), "link":re["links"].split(","), "uri":str(re["keyTerm"])}
        key.append(ke)


    return {"course":{"basic":basic, "category":cat, "lessons":lesson, "keyTerms":key, "image":image}}

@app.get("/categories")
def categories():
    query = '''
    PREFIX uexvocab: <http://www.uniandes.web.semantica.ejemplo.org/voca#>
    SELECT DISTINCT ?categoryName ?category
    WHERE {
    ?category a uexvocab:Category.
    ?category uexvocab:name ?categoryName.
    }
    '''
    result = g.query(query)
    cate = []
    for re in result:
        c = {"name":str(re["categoryName"]), "uri":str(re["category"])}
        cate.append(c)
    return {"categories":cate}

@app.post("/create_course")
async def create_course(item: dict):
    saved_item = create_course(item)
    return {"message": saved_item}

def create_course(item:dict):
    global g
    print(item)

    course = UEX["course"+item["course"]["basic"]["name"].replace(" ", "")]
    ng.add((course, RDF.type, UEXVOCAV.Course))
    ng.add((course, UEXVOCAV.name, Literal(item["course"]["basic"]["name"])))
    ng.add((course, UEXVOCAV.link, Literal(item["course"]["basic"]["link"])))
    ng.add((course, UEXVOCAV.description, Literal(item["course"]["basic"]["description"])))
    ng.add((course, UEXVOCAV.language, Literal(item["course"]["basic"]["language"])))

    ng.add((UEX[item["course"]["category"]["uri"].replace("http://www.uniandes.web.semantica.example.org/", "")], UEXVOCAV.hasCourse, course))
    ng.add((course, UEXVOCAV.courseHas, (UEX[item["course"]["category"]["uri"].replace("http://www.uniandes.web.semantica.example.org/", "")])))


    for le in item["course"]["lessons"]:
        lesson = UEX["newL"+le["name"].replace(" ", "")]
        ng.add((lesson, RDF.type, UEXVOCAV.Lesson))
        ng.add((lesson, UEXVOCAV.name, Literal(le["name"])))
        ng.add((lesson, UEXVOCAV.hasContent, Literal(le["content"])))

        ng.add((course, UEXVOCAV.hasLesson, lesson))
        ng.add((lesson, UEXVOCAV.lessonHas, course))
    

    print("Vale pa")
    conforms, results_graph, results_text = pyshacl.validate(
    data_graph=ng,
    shacl_graph=s,
    inference='rdfs'
    )

    if conforms:
        g = g+ng
        return "Curso válido en el Shape, se añadió a la ontología"
    else:
        return "Curso no válido en el Shape, no se pudo añadir a la ontología"
    
@app.get("/related-courses/{keyTerm}")
def related_courses(keyTerm:str):
    getCourses = f'''
    PREFIX uexvocab: <http://www.uniandes.web.semantica.ejemplo.org/voca#>
    PREFIX uex: <http://www.uniandes.web.semantica.example.org/>
    SELECT DISTINCT ?cuName
    WHERE {{
    ?course uexvocab:hasKeyTerm ?keyTerm.
    ?keyTerm uexvocab:hasTerm ?term.
    ?course uexvocab:name ?cuName.
    FILTER(str(?term) = "{keyTerm}")
    }}
    '''
    result = g.query(getCourses)
    ans=[]
    for r in result:
        print(r["cuName"])
        ans.append(r["cuName"])
    return {"courses":ans}