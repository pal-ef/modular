from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
import CardGenerator
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cardgen = CardGenerator.CardGenerator("phi4", "default")

class Card(BaseModel):
    text: str
    user_language: str
    target_language: str
    style: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/generate")
def generate_card(obj: Card):
    text = obj.text
    user_language = obj.user_language
    target_language = obj.target_language
    style = obj.style

    data = cardgen.generate_card(text, user_language, target_language, style)
    
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}