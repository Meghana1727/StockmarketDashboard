import pymongo
import bcrypt
import os
import certifi
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# ✅ MongoDB connection setup with fallback to local storage
class DatabaseHandler:
    def __init__(self):
        self.client = None
        self.db = None
        self.users_collection = None
        self.connected = False
        self.setup_connection()
        
    def setup_connection(self):
        """Attempt to connect to MongoDB Atlas"""
        try:
            # MongoDB Atlas credentials
            mongo_user = os.environ.get("MONGO_USER", "gorlipavanbhargav15%40gmail.com")
            mongo_pass = os.environ.get("MONGO_PASS", "Sunny%401572")
            mongo_cluster = "cluster0.ct7dekm.mongodb.net"
            mongo_db = "stock_market_dashboard"
            
            # Build connection string
            mongo_uri = f"mongodb+srv://{mongo_user}:{mongo_pass}@{mongo_cluster}/{mongo_db}?retryWrites=true&w=majority&tls=true"
            
            # Attempt connection with relaxed TLS/SSL settings
            self.client = pymongo.MongoClient(
                mongo_uri,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=5000,  # Shorter timeout to fail fast
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
                ssl_cert_reqs="CERT_NONE"  # Try with relaxed SSL verification
            )
            
            # Test connection
            self.client.admin.command('ping')
            
            # Setup collections
            self.db = self.client[mongo_db]
            self.users_collection = self.db["users"]
            self.connected = True
            print("✅ MongoDB connection successful!")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"❌ MongoDB connection failed: {e}")
            self.setup_local_fallback()
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            self.setup_local_fallback()
    
    def setup_local_fallback(self):
        """Set up in-memory storage as fallback"""
        print("⚠️ Using in-memory storage as fallback")
        self.connected = False
        self.users = {}  # In-memory user storage
    
    def add_user(self, username, password):
        """Add a new user to the database or fallback storage"""
        if not username or not password:
            print("Username or password cannot be empty")
            return False
            
        try:
            if self.connected:
                # Check if user exists in MongoDB
                if self.users_collection.find_one({"username": username}):
                    print(f"User {username} already exists")
                    return False
                
                # Hash password and store user
                hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
                self.users_collection.insert_one({
                    "username": username,
                    "password": hashed_password.decode("utf-8")
                })
            else:
                # Check if user exists in fallback storage
                if username in self.users:
                    print(f"User {username} already exists")
                    return False
                
                # Hash password and store user in fallback
                hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
                self.users[username] = {
                    "username": username,
                    "password": hashed_password.decode("utf-8")
                }
                
            print(f"✅ User {username} added successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error adding user: {e}")
            return False
    
    def get_user(self, username):
        """Get user details from database or fallback storage"""
        try:
            if self.connected:
                return self.users_collection.find_one({"username": username})
            else:
                return self.users.get(username)
        except Exception as e:
            print(f"❌ Error getting user: {e}")
            return None
    
    def verify_user(self, username, password):
        """Verify user credentials from database or fallback storage"""
        try:
            user = self.get_user(username)
            if not user or "password" not in user:
                return False
                
            stored_password = user["password"]
            if isinstance(stored_password, str):
                stored_password = stored_password.encode("utf-8")
                
            return bcrypt.checkpw(password.encode("utf-8"), stored_password)
                
        except Exception as e:
            print(f"❌ Error verifying user: {e}")
            return False
    
    def connection_status(self):
        """Return the connection status"""
        if self.connected:
            return "Connected to MongoDB Atlas"
        return "Using fallback storage (data will not persist)"

# Create a singleton instance
db_handler = DatabaseHandler()

# Export functions for easy imports
def add_user(username, password):
    return db_handler.add_user(username, password)

def get_user(username):
    return db_handler.get_user(username)

def verify_user(username, password):
    return db_handler.verify_user(username, password)

def get_connection_status():
    return db_handler.connection_status()
