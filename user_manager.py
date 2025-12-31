# user_manager.py: Manages user data and access tokens

import json

USERS_FILE = "users.json"

def load_users():
    """Loads user data from the JSON file."""
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    """Saves the users dictionary to the JSON file."""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)
