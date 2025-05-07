import random
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
#from neuralNetwork.getLevel import getUserLevel

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from typing import List
from datetime import datetime, timezone, timedelta

from Generator import Generator

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
#uri = "mongodb+srv://Modular:FlashCardsModular@cluster0.mresw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
uri = "mongodb://localhost:27017/"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

generator = Generator("phi4", "default")

def convert_to_dict(cursor):
    return [
        {**doc, "_id": str(doc["_id"])} if "_id" in doc else doc
        for doc in cursor
    ]


class Card(BaseModel):
    text: str
    owner: str
    user_language: str
    target_language: str
    style: str

class Exam(BaseModel):
    words: List[str]
    group_id: str
    user_language: str
    target_language: str
    assigned_to: str
    completed_by: str

class ExamID(BaseModel):
    id: str

class ExamResult(BaseModel):
    exam_id: str
    score: int
    total_questions: int
    user_id: str

class Deck(BaseModel):
    name: str
    user_language: str
    target_language: str
    description: str
    owner: str
    private: bool
    cards: List[str]

class DeckInfo(BaseModel):
    owner: str

class Save(BaseModel):
    deck_name: str
    deck_owner: str
    card: object
    id: str

class Fetch(BaseModel):
    deck_name: str
    deck_owner: str

class Good(BaseModel):
    id: str
    review: datetime
    retained: int
    owner: str

class UserID(BaseModel):
    id: str

collection = client['flashcards']['cards']


@app.post("/generate")
def generate_card(obj: Card):
    collection = client['flashcards']['cards']

    # Generate card
    data = generator.generate_card(obj.text, obj.user_language, obj.target_language, obj.style)
    # Add owner to card
    data["owner"] = obj.owner
    json_compatible_item_data = jsonable_encoder(data)

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


# @app.get("/decks")
# def get_decks():
#     collection = client['flashcards']['decks']
#     # TODO: Use user instead
#     return list(collection.find({"owner": "Randy"}, {'_id': 0}))

def fisher_yates_shuffle(arr):
    for i in range(len(arr) - 1, 0, -1):
        j = random.randint(0, i)  # Pick a random index from 0 to i
        arr[i], arr[j] = arr[j], arr[i]  # Swap
    return arr  # Optional, since shuffling is in-place



@app.post("/decks")
def get_decks(obj: DeckInfo):
    collection = client['flashcards']['decks']
    return list(collection.find({"owner": obj.owner}, {'_id': 0}))


@app.post("/save")
def save_deck(obj: Save):
    # First save card to database
    collection = client['flashcards']['cards']
    card = obj.card
    card["part-of"] = obj.deck_name
    card["retained"] = 1
    card["review"] = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    card["last_reviewed"] = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    queried = collection.insert_one(card)

    # Check if deck has cards, if not then assign image
    collection = client['flashcards']['decks']
    query = {"name": obj.deck_name,  "owner": obj.deck_owner, "cards": {"$ne": []}}
    has_cards = collection.find_one(query)
    
    filter_query = {"name": obj.deck_name, "owner": obj.deck_owner}
    if not has_cards:
        update_query = {"$set": {"image": card['image']}}  
        collection.update_one(filter_query, update_query)

    # Now add card to collection
    # Define filter and update
    update_query = {"$push": {"cards": obj.id}}  
    result = collection.update_one(filter_query, update_query)

    print(f"Matched: {result.matched_count}, Modified: {result.modified_count}")

    # Return good if created successfully
    return {"message": "Explicit 200"}

@app.post("/fetch-cards")
def fetch_cards(obj: Fetch):
    collection = client['flashcards']['cards']

    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) 

    filter_query = {"part-of": obj.deck_name, "owner": obj.deck_owner, "review": {"$lte": today}}
    result = collection.find(filter_query)

    result_list = convert_to_dict(result)

    return result_list

@app.post("/fetch-all-cards")
def fetch_all_cards(obj: Fetch):
    collection = client['flashcards']['cards']

    filter_query = {"part-of": obj.deck_name, "owner": obj.deck_owner}
    result = collection.find(filter_query)

    result_list = convert_to_dict(result)

    return result_list

@app.post("/good")
def good(obj: Good):
    collection = client['flashcards']['cards']

    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) 
    new_retained = int(obj.retained * 2.35)
    new_review_date = obj.review + timedelta(days=new_retained)

    filter_query = {"id": obj.id, "owner": obj.owner}
    update_query = {"$set": {"review": new_review_date, "last_reviewed": today, "retained": new_retained}}  

    # Update card to new review date and new retained days    
    result = collection.update_one(filter_query, update_query)
    
    print(f"Matched: {result.matched_count}, Modified: {result.modified_count}")
    # Return good if created successfully
    return {"message": "Explicit 200"}

@app.post("/bad")
def good(obj: Good):
    collection = client['flashcards']['cards']

    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) 
    new_review_date = today + timedelta(days=1)

    filter_query = {"id": obj.id, "owner": obj.owner}
    update_query = {"$set": {"review": new_review_date, "last_reviewed": today, "retained": 1}}  

    # Update card to new review date and new retained days    
    result = collection.update_one(filter_query, update_query)
    
    print(f"Matched: {result.matched_count}, Modified: {result.modified_count}")
    # Return good if created successfully
    return {"message": "Explicit 200"}

@app.get("/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):

    return {"item_id": item_id, "q": q}

@app.post("/pendingToday")
def pending_today(id: UserID):
    collection = client['flashcards']['cards']
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) 

    filter_query = {"owner": id.id, "review": {"$lte": today}}
    count = collection.count_documents(filter_query)

    return count

@app.get("/failed/{user_id}")
def get_failed(user_id: str):
    collection = client['modular_db']['users']
    id_mongo = ObjectId(user_id)
    filter_query = {"_id": id_mongo}
    result = collection.find_one(filter_query)
    print(result)
    return str(result["failed"])


@app.get("/failed_inc/{user_id}")
def add_fail(user_id: str):
    collection = client['modular_db']['users']
    id_mongo = ObjectId(user_id)

    filter_query = {"_id": id_mongo}
    update = {'$inc': {'failed': 1}}
    result = collection.update_one(filter_query, update)

    if result.modified_count > 0:
        print("Document updated successfully!")
    else:
        print("No document matched the query.")

    return {"message": "Explicit 200"}

def mongo_jsonable_encoder(data):
    if isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, dict):
        return {k: mongo_jsonable_encoder(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple)):
        return [mongo_jsonable_encoder(item) for item in data]
    return jsonable_encoder(data)

@app.post("/generate-exam")
def generate_exam(obj: Exam):
    collection = client['modular_db']['exams']

    # Generate exam
    exam = generator.generate_exam(obj.words, obj.user_language, obj.target_language)

    # Set extra metadata
    exam["group_id"] = obj.group_id
    exam["assigned_to"] = obj.assigned_to
    exam["completed_by"] = ""

    # Shuffle answers for each question
    for question in exam["questions"]:
        question["answers"] = fisher_yates_shuffle(question["answers"])

    res = collection.insert_one({
        "questions": exam["questions"],
        "group_id": obj.group_id,
        "assigned_to": obj.assigned_to,
        "completed_by": []
    })

    exam["id"] = str(res.inserted_id)
    json_compatible_item_data = jsonable_encoder(exam)

    return JSONResponse(content=json_compatible_item_data)

@app.post("/fetch-exam")
def fetch_exam(obj: ExamID):
    collection = client['modular_db']['exams']

    id_mongo = ObjectId(obj.id)
    filter_query = {"_id": id_mongo}
    result = collection.find_one(filter_query, {'_id': 0})

    return result

@app.post("/fetch-completed-exams")
def fetch_completed_exams(obj: UserID):
    collection = client['modular_db']['exam_results']
    cursor = collection.find({"user_id": obj.id}, {"_id": 0, "user_id": 0})
    result = convert_to_dict(cursor)
    return result

@app.post("/save-score")
def fetch_exam(obj: ExamResult):
    # Fetch exam
    collection = client['modular_db']['exams']
    id_mongo = ObjectId(obj.exam_id)
    filter_query = {"_id": id_mongo}
    update = {'$push': {'completed_by': obj.user_id}}
    result = collection.update_one(filter_query, update)

    if result.modified_count > 0:
        print("Document updated successfully!")
    else:
        print("No document matched the query.")

    collection = client['modular_db']['exam_results']

    collection.insert_one({
        "exam_id": obj.exam_id,
        "score": obj.score,
        "total_questions": obj.total_questions,
        "user_id": obj.user_id
    })

    return {"message": "Explicit 200"}

#@app.post("/user-level")
#def generate_exam(obj: User):

    # Queries para sacar la info
    #userLevel = getUserLevel(data)

    #return userLevel