from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import uuid
import os

app = Flask(__name__)

# Load environment variables
from dotenv import load_dotenv 
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://ankit05shaw:fo9Pp6frRivFkM13@cluster0.8jlnm.mongodb.net/")
client = MongoClient(MONGO_URI)
db = client["github_webhook"]
events_collection = db["events"]

# Function to insert an event
def format_event(event):
    action = event["action"].upper()
    author = event["author"]
    to_branch = event["to_branch"]
    from_branch = event.get("from_branch")  # Optional for PUSH
    timestamp = event["timestamp"]

    # Check if timestamp is already a datetime object, else parse it
    if isinstance(timestamp, str):
        timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

    formatted_timestamp = timestamp.strftime("%d %B %Y - %I:%M %p UTC")

    if action == "PUSH":
        return f'"{author}" pushed "{from_branch}" to "{to_branch}" on {formatted_timestamp}'
    elif action == "PULL":
        return f'"{author}" submitted a pull request from "{from_branch}" to "{to_branch}" on {formatted_timestamp}'
    elif action == "MERGE":
        return f'"{author}" merged branch "{from_branch}" to "{to_branch}" on {formatted_timestamp}'
    else:
        return "Unknown action"

# Function to insert an event
def insert_event(author, action, from_branch=None, to_branch=None):
    if action not in ["PUSH", "PULL", "MERGE"]:
        raise ValueError("Invalid action. Must be 'PUSH', 'PULL REQUEST', or 'MERGE'.")
 
    event = {
        "request_id": str(uuid.uuid4()),
        "author": author,
        "action": action,
        "from_branch": from_branch,
        "to_branch": to_branch,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    result = events_collection.insert_one(event)
    return str(result.inserted_id)

# Route for the webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    action = data.get("action").upper()  # Convert action to uppercase for consistency
    author = data.get("author")
    from_branch = data.get("from_branch")
    to_branch = data.get("to_branch")

    if action not in ["PUSH", "PULL", "MERGE"]:
        return jsonify({"error": "Invalid action"}), 400

    try:
        event_id = insert_event(author, action, from_branch, to_branch)
        return jsonify({"message": "Event recorded successfully", "event_id": event_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to fetch recent events
@app.route("/events", methods=["GET"])
def get_events():
    events = list(events_collection.find().sort("timestamp", -1).limit(10))
    for event in events:
        event["_id"] = str(event["_id"])  # Convert ObjectId to string
        event["formatted"] = format_event(event)  # Add formatted message
    return jsonify(events)

# Route for the homepage
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)