import pymongo
import bcrypt
from urllib.parse import quote_plus
import certifi
import os
from pymongo.server_api import ServerApi

# ✅ MongoDB Atlas Credentials
MONGO_USER = quote_plus("gorlipavanbhargav15@gmail.com")
MONGO_PASS = quote_plus("Sunny@1572")
MONGO_CLUSTER = "cluster0.ct7dekm.mongodb.net"
MONGO_DB = "stock_market_dashboard"

# ✅ Improved URI construction with retry writes
MONGO_URI = f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@{MONGO_CLUSTER}/{MONGO_DB}?retryWrites=true&w=majority"

try:
    # ✅ Connect with improved error handling and server API version
    client = pymongo.MongoClient(
        MONGO_URI,
        tlsCAFile=certifi.where(),
        server_api=ServerApi('1'),
        connectTimeoutMS=30000,
        socketTimeoutMS=30000
    )
    
    # Test connection
    client.admin.command('ping')
    print("MongoDB connection successful!")
    
    # ✅ MongoDB setup
    db = client[MONGO_DB]
    users_collection = db["users"]
    
except pymongo.errors.ConnectionFailure as e:
    print(f"Could not connect to MongoDB: {e}")
    # Provide a fallback for testing/development
    db = None
    users_collection = None

# ✅ Get user details
def get_user(username):
    try:
        if users_collection is None:
            return None
        user = users_collection.find_one({"username": username})
        if user:
            # Handle the case where password might be stored as string or bytes
            password = user["password"]
            if isinstance(password, str):
                password = password.encode("utf-8")
            return {"username": user["username"], "password": password}
        return None
    except Exception as e:
        print(f"Error retrieving user: {e}")
        return None

# ✅ Add new user with hashed password
def add_user(username, password):
    try:
        if users_collection is None:
            return False
        # Check if user exists first
        existing_user = users_collection.find_one({"username": username})
        if existing_user:
            return False
        
        # Hash password and store
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        users_collection.insert_one({
            "username": username, 
            "password": hashed_password.decode("utf-8")
        })
        return True
    except Exception as e:
        print(f"Error adding user: {e}")
        return False

# ✅ Verify user credentials
def verify_user(username, password):
    try:
        user = get_user(username)
        if not user:
            return False
        return bcrypt.checkpw(password.encode("utf-8"), user["password"])
    except Exception as e:
        print(f"Error verifying user: {e}")
        return False
