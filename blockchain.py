import json
import subprocess
import hashlib
from datetime import datetime

def log(message):
    """Helper function for logging with timestamps."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [LOG]: {message}")

def hash_password(password):
    """Hashes a password using SHA-256 for security."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(user_data):
    """Registers a user in the MultiChain blockchain if they are not already registered."""
    log(f"Received user data for registration: {user_data}")
    name = user_data["name"]
    age = user_data["age"]
    role = user_data["role"]
    password = user_data["password"]

    if not all([name, age, role, password]):
        log("Invalid user data, missing fields.")
        return None

    log(f"Checking if user {name} with role {role} already exists...")
    existing_user = get_user(name, role)
    if existing_user:
        log("User already exists. Registration aborted.")
        return None

    hashed_password = hash_password(password)
    log(f"Password hashed for security: {hashed_password}")

    user_entry = {
        "json": {
            "name": name,
            "age": age,
            "role": role,
            "password": hashed_password
        }
    }

    data_json = json.dumps(user_entry)

    command = [
        "multichain-cli", "healthcarechain", "publish", "user_stream",
        f"user_{name}_{role}", data_json
    ]

    log(f"Executing command: {' '.join(command)}")

    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            log("User registered successfully!")
            return result.stdout.strip()  # Return transaction ID
        else:
            log(f"Command Error: {result.stderr.strip()}")
            return None
    except Exception as e:
        log(f"Exception Occurred: {e}")
        return None

def get_user(name, role):
    """Fetch user details from MultiChain blockchain based on (name, role)."""
    log(f"Fetching user {name} with role {role} from blockchain...")
    command = ["multichain-cli", "healthcarechain", "liststreamitems", "user_stream"]

    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            log(f"Command Error: {result.stderr.strip()}")
            return None

        users = json.loads(result.stdout)

        for user in users:
            if "keys" in user and user["keys"][0] == f"user_{name}_{role}":
                log(f"User found: {user['data']['json']}")
                return user["data"]["json"]  # Return user details if found

    except Exception as e:
        log(f"Exception Occurred: {e}")

    log("User not found.")
    return None
