from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
import CardGenerator
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from typing import List


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

# TODO: Need to hide this
uri = "mongodb+srv://Modular:FlashCardsModular@cluster0.mresw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

cardgen = CardGenerator.CardGenerator("phi4", "default")

class Card(BaseModel):
    text: str
    user_language: str
    target_language: str
    style: str

class Deck(BaseModel):
    name: str
    user_language: str
    target_language: str
    description: str
    owner: str
    private: bool
    cards: List[str]

class Save(BaseModel):
    deck_name: str
    deck_owner: str
    card_id: str

class Fetch(BaseModel):
    deck_name: str
    deck_owner: str
    card_id: str

collection = client['flashcards']['cards']

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

    collection = client['flashcards']['cards']

    # Save into database
    print("Attempting to save to database...")
    collection.insert_one(data)

    return JSONResponse(content=json_compatible_item_data)

@app.post("/create-deck")
def create_deck(obj: Deck):
    name = obj.name
    user_language = obj.user_language
    target_language = obj.target_language
    description = obj.description

    # Save deck to database
    collection = client['flashcards']['decks']
    collection.insert_one({
        "name": name,
        "owner": obj.owner,
        "private": obj.private,
        "user_language": user_language,
        "target_language": target_language,
        "description": description,
        "cards": []
    })

    # Return good if created successfully
    return {"message": "Explicit 200"}

@app.get("/decks")
def get_decks():
    collection = client['flashcards']['decks']
    # TODO: Use user instead
    return list(collection.find({"owner": "Randy"}, {'_id': 0}))


@app.post("/save")
def create_deck(obj: Save):
    deck_name = obj.deck_name
    deck_owner = obj.deck_owner
    card_id = obj.card_id

    collection = client['flashcards']['decks']


    # Define filter and update
    filter_query = {"name": deck_name, "owner": deck_owner}
    update_query = {"$push": {"cards": card_id}}  
    result = collection.update_one(filter_query, update_query)

    print(f"Matched: {result.matched_count}, Modified: {result.modified_count}")

    # Return good if created successfully
    return {"message": "Explicit 200"}

@app.post("/fetch-cards")
def create_deck(obj: Fetch):
    deck_owner = obj.deck_owner
    deck_name = obj.deck_name

    collection = client['flashcards']['cards']

    filter_query = {"part_of": deck_name, "owner": deck_owner}
    result = collection.find(filter_query)

    return result


@app.get("/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):

    return {"item_id": item_id, "q": q}