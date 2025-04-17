import pymongo
import bcrypt
import os
import certifi
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import time

# Global variables
client = None
db = None
users_collection = None
connected = False
in_memory_users = {}  # Fallback storage

# ✅ Configure MongoDB connection
def configure_mongodb():
    global client, db, users_collection, connected, in_memory_users
    
    try:
        # MongoDB Atlas credentials (URL-encoded)
        mongo_user = "gorlipavanbhargav15%40gmail.com"
        mongo_pass = "Sunny%401572"
        mongo_cluster = "cluster0.ct7dekm.mongodb.net"
        mongo_db = "stock_market_dashboard"
        
        # Build connection string
        mongo_uri = f"mongodb+srv://{mongo_user}:{mongo_pass}@{mongo_cluster}/{mongo_db}?retryWrites=true&w=majority"
        
        # Connect with relaxed SSL settings
        client = pymongo.MongoClient(
            mongo_uri,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            ssl_cert_reqs="CERT_NONE"  # Disable strict SSL certificate verification
        )
        
        # Test connection
        client.admin.command('ping')
        
        # Setup DB
        db = client[mongo_db]
        users_collection = db["users"]
        connected = True
        print("✅ MongoDB connection successful!")
        return True
        
    except Exception as e:
        print(f"⚠️ MongoDB connection failed: {e}")
        connected = False
        return False

# Try to connect on import
try:
    connected = configure_mongodb()
except:
    connected = False
    print("⚠️ Using fallback in-memory storage")

# ✅ Add user function
def add_user(username, password):
    global connected, in_memory_users
    
    # Validate inputs
    if not username or not password:
        return False
    
    try:
        # Try to reconnect if needed
        if not connected:
            connected = configure_mongodb()
        
        if connected:
            # Using MongoDB
            if users_collection.find_one({"username": username}):
                return False
                
            # Hash password
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            
            # Insert user
            users_collection.insert_one({
                "username": username,
                "password": hashed_password.decode("utf-8"),
                "created_at": time.time()
            })
            return True
            
        else:
            # Using fallback storage
            if username in in_memory_users:
                return False
                
            # Hash password
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            
            # Store user in memory
            in_memory_users[username] = {
                "username": username,
                "password": hashed_password.decode("utf-8"),
                "created_at": time.time()
            }
            return True
            
    except Exception as e:
        print(f"Error adding user: {e}")
        return False

# ✅ Verify user function
def verify_user(username, password):
    global connected, in_memory_users
    
    # Validate inputs
    if not username or not password:
        return False
    
    try:
        # Try to reconnect if needed
        if not connected:
            connected = configure_mongodb()
        
        user = None
        
        if connected:
            # Using MongoDB
            user = users_collection.find_one({"username": username})
        else:
            # Using fallback storage
            user = in_memory_users.get(username)
        
        if not user or "password" not in user:
            return False
            
        # Get stored password
        stored_password = user["password"]
        if isinstance(stored_password, str):
            stored_password = stored_password.encode("utf-8")
            
        # Verify password
        return bcrypt.checkpw(password.encode("utf-8"), stored_password)
        
    except Exception as e:
        print(f"Error verifying user: {e}")
        return False

# ✅ Get user function
def get_user(username):
    global connected, in_memory_users
    
    try:
        # Try to reconnect if needed
        if not connected:
            connected = configure_mongodb()
        
        if connected:
            # Using MongoDB
            return users_collection.find_one({"username": username})
        else:
            # Using fallback storage
            return in_memory_users.get(username)
            
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

# ✅ Get connection status
def get_connection_status():
    global connected
    return connected
