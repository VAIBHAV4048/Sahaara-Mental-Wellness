import json
import os

DATABASE_FILE = "db.json"

def get_db():
    """Reads the database file and returns its content."""
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'w') as f:
            json.dump([], f)
    with open(DATABASE_FILE, 'r') as f:
        return json.load(f)

def save_db(data):
    """Saves the given data to the database file."""
    with open(DATABASE_FILE, 'w') as f:
        json.dump(data, f, indent=4)
