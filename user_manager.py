# user_manager.py: Manages user data and access tokens

import json
import streamlit as st

USERS_FILE = "users.json"

def load_users():
    """
    Loads user profiles.
    In Streamlit Cloud, it loads from st.secrets.
    For local development, it falls back to users.json.
    """
    # Prefer loading from Streamlit secrets if the app is deployed
    if hasattr(st, 'secrets') and "shopee_profiles" in st.secrets:
        return json.loads(st.secrets["shopee_profiles"])

    # Fallback to local users.json file for local development
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # This is expected if the file hasn't been created yet locally.
        return {}
    except json.JSONDecodeError:
        # This indicates a corrupted file.
        print(f"Warning: Could not parse {USERS_FILE}. Returning empty profiles.")
        return {}


def save_users(users):
    """Saves the users dictionary to the JSON file (for local use only)."""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)
