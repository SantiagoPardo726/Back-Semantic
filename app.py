from typing import Union

from fastapi import FastAPI

from functions import images

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

