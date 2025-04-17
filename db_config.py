import pymongo
import bcrypt
from urllib.parse import quote_plus
import certifi

# ✅ MongoDB Atlas Credentials
MONGO_USER = quote_plus("gorlipavanbhargav15@gmail.com")
MONGO_PASS = quote_plus("Sunny@1572")  # 👈 This will encode @ as %40
MONGO_CLUSTER = "cluster0.ct7dekm.mongodb.net"
MONGO_DB = "stock_market_dashboard"

# ✅ Proper URI construction
MONGO_URI = f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@{MONGO_CLUSTER}/{MONGO_DB}/"

# ✅ Connect with TLS cert verification
client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())

# ✅ MongoDB setup
db = client[MONGO_DB]
users_collection = db["users"]

# ✅ Get user details
def get_user(username):
    user = users_collection.find_one({"username": username})
    if user:
        return {"username": user["username"], "password": user["password"].encode("utf-8")}
    return None

# ✅ Add new user with hashed password
def add_user(username, password):
    if users_collection.find_one({"username": username}):
        return False
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    users_collection.insert_one({"username": username, "password": hashed_password})
    return True

# ✅ Verify user credentials
def verify_user(username, password):
    user = get_user(username)
    return user and bcrypt.checkpw(password.encode("utf-8"), user["password"])
