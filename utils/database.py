"""
========================================================================
   EDUSHIELD: DATABASE UTILITY LAYER (MongoDB Atlas + SQLite Fallback)
   database.py: Schema management and query functions for MongoDB Atlas,
                with automatic fallback to local SQLite.
========================================================================
"""

import os
import sqlite3
import json
import logging
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# Try importing PyMongo
try:
    from pymongo import MongoClient
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False

logger = logging.getLogger(__name__)

# Base Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'edushield.db')

# MongoDB Configuration
MONGO_URI = os.environ.get(
    'MONGO_URI', 
    'mongodb+srv://danushkumardk07_db_user:danushkumar%405995@cluster0.22gafw4.mongodb.net/?retryWrites=true&w=majority&appName=EduShield'
)
MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME', 'edushield')

_mongo_client = None
_mongo_connected = None

class User(UserMixin):
    """User Model representing authentication accounts."""
    def __init__(self, id, username, email, role, created_at):
        self.id = id
        self.username = username
        self.email = email
        self.role = role
        self.created_at = created_at

def get_mongo_db():
    """Returns connected MongoDB database instance, or None if unavailable."""
    global _mongo_client, _mongo_connected
    if not PYMONGO_AVAILABLE:
        return None
        
    if _mongo_client is None:
        try:
            _mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
            _mongo_client.admin.command('ping')
            _mongo_connected = True
            print("[+] Connected to MongoDB Atlas successfully!")
        except Exception as e:
            logger.warning(f"MongoDB Atlas connection failed: {e}. Falling back to SQLite.")
            _mongo_client = None
            _mongo_connected = False
            return None
            
    return _mongo_client[MONGO_DB_NAME] if _mongo_connected else None

def get_db_connection():
    """Returns a connection to the SQLite database with dict factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes schemas and default users in both MongoDB and SQLite."""
    # 1. Initialize SQLite
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prediction_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            student_name TEXT,
            student_id TEXT,
            prediction TEXT NOT NULL,
            probability REAL NOT NULL,
            confidence REAL NOT NULL,
            risk_level TEXT NOT NULL,
            input_data_json TEXT NOT NULL,
            recommendations_json TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        admin_pass = generate_password_hash('admin123')
        user_pass = generate_password_hash('user123')
        cursor.execute("INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                       ('admin', 'admin@edushield.com', admin_pass, 'admin'))
        cursor.execute("INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                       ('user', 'user@edushield.com', user_pass, 'user'))
        conn.commit()
    conn.close()

    # 2. Initialize MongoDB Atlas (if available)
    mongo_db = get_mongo_db()
    if mongo_db is not None:
        try:
            # Ensure unique indexes
            mongo_db["users"].create_index("username", unique=True)
            mongo_db["users"].create_index("id", unique=True)
            mongo_db["prediction_history"].create_index("id", unique=True)

            if mongo_db["users"].count_documents({}) == 0:
                admin_pass = generate_password_hash('admin123')
                user_pass = generate_password_hash('user123')
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                mongo_db["users"].insert_many([
                    {'id': 1, 'username': 'admin', 'email': 'admin@edushield.com', 'password_hash': admin_pass, 'role': 'admin', 'created_at': now},
                    {'id': 2, 'username': 'user', 'email': 'user@edushield.com', 'password_hash': user_pass, 'role': 'user', 'created_at': now}
                ])
                print("[+] Pre-populated default accounts in MongoDB Atlas: admin/admin123 and user/user123.")
        except Exception as e:
            logger.error(f"Error initializing MongoDB Atlas schema: {e}")

# ----------------- User Auth Queries -----------------

def get_user_by_id(user_id):
    """Loads a user by primary key ID (used by Flask-Login)."""
    mongo_db = get_mongo_db()
    if mongo_db is not None:
        try:
            doc = mongo_db["users"].find_one({"id": int(user_id)})
            if doc:
                return User(doc['id'], doc['username'], doc['email'], doc['role'], doc['created_at'])
        except Exception as e:
            logger.error(f"MongoDB error in get_user_by_id: {e}")

    conn = get_db_connection()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if row:
        return User(row['id'], row['username'], row['email'], row['role'], row['created_at'])
    return None

def get_user_by_username(username):
    """Loads a user by username and validates credentials."""
    mongo_db = get_mongo_db()
    if mongo_db is not None:
        try:
            doc = mongo_db["users"].find_one({"username": username})
            if doc:
                return doc
        except Exception as e:
            logger.error(f"MongoDB error in get_user_by_username: {e}")

    conn = get_db_connection()
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def create_user(username, email, password, role='user'):
    """Registers a new user account with hashed password."""
    pass_hash = generate_password_hash(password)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_id = None

    mongo_db = get_mongo_db()
    if mongo_db is not None:
        try:
            # Check existing username
            if mongo_db["users"].find_one({"username": username}):
                return None
            highest = mongo_db["users"].find_one(sort=[("id", -1)])
            next_id = (highest["id"] + 1) if highest and "id" in highest else 1
            user_doc = {
                "id": next_id,
                "username": username,
                "email": email,
                "password_hash": pass_hash,
                "role": role,
                "created_at": now
            }
            mongo_db["users"].insert_one(user_doc)
            user_id = next_id
        except Exception as e:
            logger.error(f"MongoDB error in create_user: {e}")

    # Mirror to SQLite for fallback persistence
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)",
            (username, email, pass_hash, role, now)
        )
        conn.commit()
        if user_id is None:
            user_id = cursor.lastrowid
        conn.close()
    except Exception:
        pass

    return user_id

def get_all_users_count():
    """Returns total registered users."""
    mongo_db = get_mongo_db()
    if mongo_db is not None:
        try:
            return mongo_db["users"].count_documents({})
        except Exception as e:
            logger.error(f"MongoDB error in get_all_users_count: {e}")

    conn = get_db_connection()
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    return count

# ----------------- Predictions Queries -----------------

def add_prediction(user_id, student_name, student_id, prediction, probability, confidence, risk_level, input_dict, recs_list):
    """Saves a student dropout risk assessment entry to history."""
    input_json = json.dumps(input_dict) if isinstance(input_dict, dict) else input_dict
    recs_json = json.dumps(recs_list) if isinstance(recs_list, list) else recs_list
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pred_id = None

    mongo_db = get_mongo_db()
    if mongo_db is not None:
        try:
            highest = mongo_db["prediction_history"].find_one(sort=[("id", -1)])
            next_id = (highest["id"] + 1) if highest and "id" in highest else 1
            pred_doc = {
                "id": next_id,
                "user_id": int(user_id),
                "student_name": student_name,
                "student_id": student_id,
                "prediction": prediction,
                "probability": float(probability),
                "confidence": float(confidence),
                "risk_level": risk_level,
                "input_data_json": input_json,
                "recommendations_json": recs_json,
                "created_at": now
            }
            mongo_db["prediction_history"].insert_one(pred_doc)
            pred_id = next_id
        except Exception as e:
            logger.error(f"MongoDB error in add_prediction: {e}")

    # Mirror to SQLite
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO prediction_history 
            (user_id, student_name, student_id, prediction, probability, confidence, risk_level, input_data_json, recommendations_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, student_name, student_id, prediction, probability, confidence, risk_level, input_json, recs_json, now))
        conn.commit()
        if pred_id is None:
            pred_id = cursor.lastrowid
        conn.close()
    except Exception:
        pass

    return pred_id

def get_prediction_by_id(pred_id):
    """Loads a single prediction history record by ID."""
    mongo_db = get_mongo_db()
    if mongo_db is not None:
        try:
            doc = mongo_db["prediction_history"].find_one({"id": int(pred_id)})
            if doc:
                record = dict(doc)
                # Lookup analyst name
                user_doc = mongo_db["users"].find_one({"id": record.get("user_id")})
                record['analyst_name'] = user_doc['username'] if user_doc else 'Unknown'
                record['input_data'] = json.loads(record['input_data_json']) if isinstance(record['input_data_json'], str) else record['input_data_json']
                record['recommendations'] = json.loads(record['recommendations_json']) if isinstance(record['recommendations_json'], str) else record['recommendations_json']
                return record
        except Exception as e:
            logger.error(f"MongoDB error in get_prediction_by_id: {e}")

    conn = get_db_connection()
    row = conn.execute('''
        SELECT p.*, u.username as analyst_name 
        FROM prediction_history p 
        LEFT JOIN users u ON p.user_id = u.id 
        WHERE p.id = ?
    ''', (pred_id,)).fetchone()
    conn.close()
    if row:
        record = dict(row)
        record['input_data'] = json.loads(record['input_data_json'])
        record['recommendations'] = json.loads(record['recommendations_json'])
        return record
    return None

def get_predictions(user_id=None, search=None, course=None, risk_level=None, limit=20, offset=0):
    """Retrieves prediction history entries with filters, search, and pagination."""
    mongo_db = get_mongo_db()
    if mongo_db is not None:
        try:
            q = {}
            if user_id:
                q["user_id"] = int(user_id)
            if risk_level:
                q["risk_level"] = risk_level
            if search:
                q["$or"] = [
                    {"student_name": {"$regex": search, "$options": "i"}},
                    {"student_id": {"$regex": search, "$options": "i"}}
                ]

            cursor = mongo_db["prediction_history"].find(q).sort("created_at", -1).skip(offset).limit(limit)
            results = []
            
            # Cache analyst names for quick lookup
            user_map = {u["id"]: u["username"] for u in mongo_db["users"].find({}, {"id": 1, "username": 1})}
            
            for doc in cursor:
                d = dict(doc)
                d['analyst_name'] = user_map.get(d.get('user_id'), 'Unknown')
                d['input_data'] = json.loads(d['input_data_json']) if isinstance(d.get('input_data_json'), str) else d.get('input_data_json', {})
                d['recommendations'] = json.loads(d['recommendations_json']) if isinstance(d.get('recommendations_json'), str) else d.get('recommendations_json', [])
                results.append(d)
            return results
        except Exception as e:
            logger.error(f"MongoDB error in get_predictions: {e}")

    conn = get_db_connection()
    query = '''
        SELECT p.*, u.username as analyst_name 
        FROM prediction_history p 
        LEFT JOIN users u ON p.user_id = u.id 
        WHERE 1=1
    '''
    params = []
    if user_id:
        query += " AND p.user_id = ?"
        params.append(user_id)
    if search:
        query += " AND (p.student_name LIKE ? OR p.student_id LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    if risk_level:
        query += " AND p.risk_level = ?"
        params.append(risk_level)

    query += " ORDER BY p.created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = conn.execute(query, params).fetchall()
    conn.close()

    results = []
    for r in rows:
        d = dict(r)
        d['input_data'] = json.loads(d['input_data_json'])
        d['recommendations'] = json.loads(d['recommendations_json'])
        results.append(d)
    return results

def get_predictions_count(user_id=None, search=None, risk_level=None):
    """Returns the total number of filtered predictions (for pagination counts)."""
    mongo_db = get_mongo_db()
    if mongo_db is not None:
        try:
            q = {}
            if user_id:
                q["user_id"] = int(user_id)
            if risk_level:
                q["risk_level"] = risk_level
            if search:
                q["$or"] = [
                    {"student_name": {"$regex": search, "$options": "i"}},
                    {"student_id": {"$regex": search, "$options": "i"}}
                ]
            return mongo_db["prediction_history"].count_documents(q)
        except Exception as e:
            logger.error(f"MongoDB error in get_predictions_count: {e}")

    conn = get_db_connection()
    query = "SELECT COUNT(*) FROM prediction_history WHERE 1=1"
    params = []
    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)
    if search:
        query += " AND (student_name LIKE ? OR student_id LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    if risk_level:
        query += " AND risk_level = ?"
        params.append(risk_level)

    count = conn.execute(query, params).fetchone()[0]
    conn.close()
    return count

def delete_prediction(pred_id):
    """Deletes a prediction record."""
    mongo_db = get_mongo_db()
    if mongo_db is not None:
        try:
            mongo_db["prediction_history"].delete_one({"id": int(pred_id)})
        except Exception as e:
            logger.error(f"MongoDB error in delete_prediction: {e}")

    conn = get_db_connection()
    conn.execute("DELETE FROM prediction_history WHERE id = ?", (pred_id,))
    conn.commit()
    conn.close()

# ----------------- Dashboard Analytics Stats -----------------

def get_system_stats():
    """Computes global platform performance metrics (Admin dashboard)."""
    mongo_db = get_mongo_db()
    if mongo_db is not None:
        try:
            total_users = mongo_db["users"].count_documents({})
            total_preds = mongo_db["prediction_history"].count_documents({})
            high_risk = mongo_db["prediction_history"].count_documents({"risk_level": "High"})
            medium_risk = mongo_db["prediction_history"].count_documents({"risk_level": "Medium"})
            low_risk = mongo_db["prediction_history"].count_documents({"risk_level": "Low"})

            # Avg confidence
            pipeline = [{"$group": {"_id": None, "avg_conf": {"$avg": "$confidence"}}}]
            agg = list(mongo_db["prediction_history"].aggregate(pipeline))
            avg_conf = round(agg[0]["avg_conf"], 2) if agg and agg[0].get("avg_conf") is not None else 85.0

            # Recent 10
            user_map = {u["id"]: u["username"] for u in mongo_db["users"].find({}, {"id": 1, "username": 1})}
            recent_cursor = mongo_db["prediction_history"].find().sort("created_at", -1).limit(10)
            recent_predictions = []
            for doc in recent_cursor:
                d = dict(doc)
                d['analyst_name'] = user_map.get(d.get('user_id'), 'Unknown')
                recent_predictions.append(d)

            return {
                "total_users": total_users,
                "total_predictions": total_preds,
                "high_risk_count": high_risk,
                "medium_risk_count": medium_risk,
                "low_risk_count": low_risk,
                "avg_confidence": avg_conf,
                "recent_predictions": recent_predictions
            }
        except Exception as e:
            logger.error(f"MongoDB error in get_system_stats: {e}")

    conn = get_db_connection()
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_preds = conn.execute("SELECT COUNT(*) FROM prediction_history").fetchone()[0]
    high_risk = conn.execute("SELECT COUNT(*) FROM prediction_history WHERE risk_level='High'").fetchone()[0]
    medium_risk = conn.execute("SELECT COUNT(*) FROM prediction_history WHERE risk_level='Medium'").fetchone()[0]
    low_risk = conn.execute("SELECT COUNT(*) FROM prediction_history WHERE risk_level='Low'").fetchone()[0]
    avg_conf_row = conn.execute("SELECT AVG(confidence) FROM prediction_history").fetchone()
    avg_conf = round(avg_conf_row[0], 2) if avg_conf_row[0] is not None else 85.0

    recent_rows = conn.execute('''
        SELECT p.*, u.username as analyst_name 
        FROM prediction_history p
        LEFT JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC LIMIT 10
    ''').fetchall()
    recent_predictions = [dict(r) for r in recent_rows]
    conn.close()

    return {
        "total_users": total_users,
        "total_predictions": total_preds,
        "high_risk_count": high_risk,
        "medium_risk_count": medium_risk,
        "low_risk_count": low_risk,
        "avg_confidence": avg_conf,
        "recent_predictions": recent_predictions
    }

def get_user_stats(user_id):
    """Computes statistics for a specific analyst (User dashboard)."""
    mongo_db = get_mongo_db()
    if mongo_db is not None:
        try:
            uid = int(user_id)
            total_preds = mongo_db["prediction_history"].count_documents({"user_id": uid})
            high_risk = mongo_db["prediction_history"].count_documents({"user_id": uid, "risk_level": "High"})
            medium_risk = mongo_db["prediction_history"].count_documents({"user_id": uid, "risk_level": "Medium"})
            low_risk = mongo_db["prediction_history"].count_documents({"user_id": uid, "risk_level": "Low"})

            recent_cursor = mongo_db["prediction_history"].find({"user_id": uid}).sort("created_at", -1).limit(5)
            recent_predictions = [dict(doc) for doc in recent_cursor]

            return {
                "total_predictions": total_preds,
                "high_risk_count": high_risk,
                "medium_risk_count": medium_risk,
                "low_risk_count": low_risk,
                "recent_predictions": recent_predictions
            }
        except Exception as e:
            logger.error(f"MongoDB error in get_user_stats: {e}")

    conn = get_db_connection()
    total_preds = conn.execute("SELECT COUNT(*) FROM prediction_history WHERE user_id = ?", (user_id,)).fetchone()[0]
    high_risk = conn.execute("SELECT COUNT(*) FROM prediction_history WHERE user_id = ? AND risk_level='High'", (user_id,)).fetchone()[0]
    medium_risk = conn.execute("SELECT COUNT(*) FROM prediction_history WHERE user_id = ? AND risk_level='Medium'", (user_id,)).fetchone()[0]
    low_risk = conn.execute("SELECT COUNT(*) FROM prediction_history WHERE user_id = ? AND risk_level='Low'", (user_id,)).fetchone()[0]

    recent_rows = conn.execute('''
        SELECT * FROM prediction_history 
        WHERE user_id = ? 
        ORDER BY created_at DESC LIMIT 5
    ''', (user_id,)).fetchall()
    recent_predictions = [dict(r) for r in recent_rows]
    conn.close()

    return {
        "total_predictions": total_preds,
        "high_risk_count": high_risk,
        "medium_risk_count": medium_risk,
        "low_risk_count": low_risk,
        "recent_predictions": recent_predictions
    }
