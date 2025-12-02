from tinydb import TinyDB, Query
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from config import Config

# Database setup
db = TinyDB(Config.DATABASE_NAME)
users_table = db.table('users')
documents_table = db.table('documents')

# ==================== AI FUNCTION ====================
def call_ai_api(prompt):
    """
    Replace this function body with your LLM API call
    Arguments: prompt (string) - the input prompt
    Returns: string - AI response
    """
    # TODO: Add your API call here
    return f"[AI Response Placeholder]\n\nYou sent: {prompt}\n\nReplace call_ai_api() function in models.py with your actual LLM API call."

# ==================== USER FUNCTIONS ====================
def create_user(username, password):
    """Create a new user"""
    User = Query()
    if users_table.search(User.username == username):
        return None
    
    users_table.insert({
        'username': username,
        'password': generate_password_hash(password)
    })
    return True

def get_user(username):
    """Get user by username"""
    User = Query()
    users = users_table.search(User.username == username)
    return users[0] if users else None

def verify_password(user, password):
    """Verify user password"""
    return check_password_hash(user['password'], password)

# ==================== DOCUMENT FUNCTIONS ====================
def save_document(user_id, doc_type, input_text, output_text):
    """Save document to history"""
    doc = {
        'doc_id': str(datetime.now().timestamp()),
        'user_id': user_id,
        'type': doc_type,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'input': input_text,
        'output': output_text,
        'preview': input_text[:50] + '...' if len(input_text) > 50 else input_text
    }
    documents_table.insert(doc)
    return doc

def get_user_documents(user_id):
    """Get all documents for a user"""
    Doc = Query()
    return documents_table.search(Doc.user_id == user_id)

def get_document(doc_id, user_id):
    """Get a specific document"""
    Doc = Query()
    docs = documents_table.search(
        (Doc.doc_id == doc_id) & (Doc.user_id == user_id)
    )
    return docs[0] if docs else None

def delete_document(doc_id, user_id):
    """Delete a document"""
    Doc = Query()
    documents_table.remove(
        (Doc.doc_id == doc_id) & (