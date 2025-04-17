import pymongo
import bcrypt
from urllib.parse import quote_plus
import certifi
import time
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# ✅ MongoDB Atlas Credentials
MONGO_USER = quote_plus("gorlipavanbhargav15@gmail.com")
MONGO_PASS = quote_plus("Sunny@1572")
MONGO_CLUSTER = "cluster0.ct7dekm.mongodb.net"
MONGO_DB = "stock_market_dashboard"

# ✅ Improved URI construction
MONGO_URI = f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@{MONGO_CLUSTER}/{MONGO_DB}?retryWrites=true&w=majority"

# Global connection flag
connected = False
client = None
db = None
users_collection = None

def connect_to_mongodb():
    global client, db, users_collection, connected
    
    if connected:
        return True
        
    try:
        # ✅ Connect with improved parameters
        client = pymongo.MongoClient(
            MONGO_URI,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=20000,
            socketTimeoutMS=20000,
            server_api=ServerApi('1')
        )
        
        # Force connection attempt
        client.server_info()
        
        # If we got here, connection successful
        db = client[MONGO_DB]
        users_collection = db["users"]
        
        # Create index to enforce unique usernames
        users_collection.create_index([("username", pymongo.ASCENDING)], unique=True)
        
        connected = True
        print("MongoDB connection successful!")
        return True
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"MongoDB connection failed: {e}")
        connected = False
        return False
    except Exception as e:
        print(f"Unexpected error connecting to MongoDB: {e}")
        connected = False
        return False

# Try initial connection
connect_to_mongodb()

# ✅ Get user details with retry logic
def get_user(username):
    if not connected and not connect_to_mongodb():
        return None
        
    try:
        return users_collection.find_one({"username": username})
    except Exception as e:
        print(f"Error getting user: {e}")
        connected = False
        return None

# ✅ Add new user with robust error handling
def add_user(username, password):
    if not username or not password:
        print("Username or password cannot be empty")
        return False
        
    if not connected and not connect_to_mongodb():
        print("Cannot connect to database")
        return False
        
    try:
        # Check if user exists
        existing_user = users_collection.find_one({"username": username})
        if existing_user:
            print(f"User {username} already exists")
            return False
            
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        
        # Insert user
        result = users_collection.insert_one({
            "username": username,
            "password": hashed_password.decode("utf-8"),
            "created_at": time.time()
        })
        
        return result.acknowledged
        
    except pymongo.errors.DuplicateKeyError:
        print(f"User {username} already exists (race condition)")
        return False
    except Exception as e:
        print(f"Error adding user: {e}")
        connected = False
        return False

# ✅ Verify user with retry logic
def verify_user(username, password):
    if not connected and not connect_to_mongodb():
        return False
        
    try:
        user = get_user(username)
        if not user or "password" not in user:
            return False
            
        stored_password = user["password"]
        if isinstance(stored_password, str):
            stored_password = stored_password.encode("utf-8")
            
        return bcrypt.checkpw(password.encode("utf-8"), stored_password)
        
    except Exception as e:
        print(f"Error verifying user: {e}")
        connected = False
        return False
