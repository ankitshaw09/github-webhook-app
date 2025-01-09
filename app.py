from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(__name__)

# Load environment variables
from dotenv import load_dotenv 
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://ankit05shaw:fo9Pp6frRivFkM13@cluster0.8jlnm.mongodb.net/")
client = MongoClient(MONGO_URI)
db = client["github_webhook"]
events_collection = db["events"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    action = data.get("action")
    author = data.get("author")
    from_branch = data.get("from_branch")
    to_branch = data.get("to_branch")
    timestamp = datetime.utcnow().strftime("%d %b %Y - %I:%M %p UTC")
    
    if action == "push":
        message = f'"{author}" pushed to "{to_branch}" on {timestamp}'
    elif action == "pull_request":
        message = f'"{author}" submitted a pull request from "{from_branch}" to "{to_branch}" on {timestamp}'
    elif action == "merge":
        message = f'"{author}" merged branch "{from_branch}" to "{to_branch}" on {timestamp}'
    else:
        return jsonify({"error": "Invalid action"}), 400

    event = {
        "action": action,
        "author": author,
        "message": message,
        "timestamp": datetime.utcnow()
    }
    events_collection.insert_one(event)
    return jsonify({"message": "Event recorded successfully"}), 200

@app.route("/events", methods=["GET"])
def get_events():
    events = list(events_collection.find().sort("timestamp", -1).limit(10))
    for event in events:
        event["_id"] = str(event["_id"])
    return jsonify(events)

if __name__ == "__main__":
    app.run(debug=True)
