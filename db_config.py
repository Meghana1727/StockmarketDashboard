import pymongo
import bcrypt
import os
from urllib.parse import quote_plus

# ✅ MongoDB Atlas Connection
# Replace these with your actual MongoDB Atlas credentials
MONGO_USER = quote_plus("gorlipavanbhargav15@gmail.com")
MONGO_PASS = quote_plus("Sunny@1572")
MONGO_CLUSTER = "cluster0.ct7dekm.mongodb.net"  # Your actual cluster hostname
MONGO_DB = "stock_market_dashboard"

# ✅ Construct the full MongoDB URI
MONGO_URI = f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@{MONGO_CLUSTER}/?retryWrites=true&w=majority"

# ✅ Connect to MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB]
users_collection = db["users"]

# ✅ Function to fetch user details
def get_user(username):
    """Retrieve user details from MongoDB."""
    user = users_collection.find_one({"username": username})
    if user:
        return {"username": user["username"], "password": user["password"].encode("utf-8")}
    return None

# ✅ Function to add a new user (with hashed password)
def add_user(username, password):
    """Register a new user with hashed password."""
    if users_collection.find_one({"username": username}):
        return False  # Username already exists
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    users_collection.insert_one({"username": username, "password": hashed_password})
    return True

# ✅ Function to verify user login
def verify_user(username, password):
    """Check if the entered password matches the stored hashed password."""
    user = get_user(username)
    if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        return True
    return False
