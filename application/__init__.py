from flask import Flask
from pymongo import MongoClient
from dotenv import load_dotenv
from os import getenv

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = getenv("SECRET_KEY")
app.config["MONGO_URI"] = getenv("MONGO_URI")

client = MongoClient(app.config["MONGO_URI"])
db = client.users

todos = db.todos
posts = db.posts

from application import routes
