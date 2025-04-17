import pymongo
import bcrypt
from urllib.parse import quote_plus
import certifi

# ✅ MongoDB Atlas Credentials (HARD-CODED — for demo/testing only)
MONGO_USER = quote_plus("gorlipavanbhargav15@gmail.com")
MONGO_PASS = quote_plus("Sunny@1572")
MONGO_CLUSTER = "cluster0.ct7dekm.mongodb.net"
MONGO_DB = "stock_market_dashboard"

# ✅ MongoDB URI with SSL
MONGO_URI = f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@{MONGO_CLUSTER}/?retryWrites=true&w=majority&ssl=true"

# ✅ Connect with TLS certificate verification (IMPORTANT!)
client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())

# ✅ Select DB and Collection
db = client[MONGO_DB]
users_collection = db["users"]

# ✅ Get user details
def get_user(username):
    """Retrieve user details from MongoDB."""
    user = users_collection.find_one({"username": username})
    if user:
        return {"username": user["username"], "password": user["password"].encode("utf-8")}
    return None

# ✅ Add new user with hashed password
def add_user(username, password):
    """Register a new user with hashed password."""
    if users_collection.find_one({"username": username}):
        return False  # Username already exists
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    users_collection.insert_one({"username": username, "password": hashed_password})
    return True

# ✅ Verify user credentials
def verify_user(username, password):
    """Check if the entered password matches the stored hashed password."""
    user = get_user(username)
    if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        return True
    return False
