from tinydb import TinyDB, Query
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import config
import os
import ai_service

# Ensure data directories exist
os.makedirs(os.path.dirname(config.USERS_DATABASE), exist_ok=True)
os.makedirs(config.DOCUMENTS_FOLDER, exist_ok=True)

# Initialize users database
users_db = TinyDB(config.USERS_DATABASE)
users_table = users_db.table('users')

# ==================== USER FUNCTIONS ====================
def create_user(username, password):
    """Create a new user"""
    User = Query()
    if users_table.search(User.username == username):
        return False
    
    users_table.insert({
        'username': username,
        'password': generate_password_hash(password)
    })
    return True

def get_user(username):
    """Get user by username - returns dict with doc_id"""
    User = Query()
    users = users_table.search(User.username == username)
    if users:
        user_data = users[0]
        # TinyDB stores doc_id separately, we need to get it
        user_with_id = users_table.get(Query().username == username)
        return user_with_id
    return None

def verify_password(user, password):
    """Verify user password"""
    return check_password_hash(user['password'], password)

# ==================== DOCUMENT FUNCTIONS ====================
def _get_user_db(user_id):
    """Get or create user-specific document database"""
    db_path = os.path.join(config.DOCUMENTS_FOLDER, f'user_{user_id}.json')
    return TinyDB(db_path)

def save_document(user_id, doc_type, input_text, output_text):
    """Save document to user-specific database with risk scoring"""
    user_db = _get_user_db(user_id)
    documents_table = user_db.table('documents')
    
    # Calculate risk score for relevant document types
    risk_score = None
    if doc_type in ['Contract Review', 'Document Analysis', 'Document Comparison']:
        risk_score = ai_service.get_risk_score(input_text)
    
    doc = {
        'doc_id': str(datetime.now().timestamp()),
        'user_id': user_id,
        'type': doc_type,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'input': input_text,
        'output': output_text,
        'risk_score': risk_score,
        'preview': input_text[:50] + '...' if len(input_text) > 50 else input_text
    }
    documents_table.insert(doc)
    user_db.close()
    return doc

def get_user_documents(user_id):
    """Get all documents for a user"""
    user_db = _get_user_db(user_id)
    documents_table = user_db.table('documents')
    docs = documents_table.all()
    user_db.close()
    # Sort by date, newest first
    return sorted(docs, key=lambda x: x.get('date', ''), reverse=True)

def get_document(doc_id, user_id):
    """Get a specific document"""
    user_db = _get_user_db(user_id)
    documents_table = user_db.table('documents')
    Doc = Query()
    
    # Debug: print what we're looking for
    print(f"[DEBUG] Looking for doc_id: {doc_id} (type: {type(doc_id)})")
    print(f"[DEBUG] For user_id: {user_id}")
    
    # Get all docs to see what's there
    all_docs = documents_table.all()
    print(f"[DEBUG] Total documents in DB: {len(all_docs)}")
    if all_docs:
        print(f"[DEBUG] Sample doc_id from DB: {all_docs[0].get('doc_id')} (type: {type(all_docs[0].get('doc_id'))})")
    
    # Search for the document
    docs = documents_table.search(Doc.doc_id == str(doc_id))
    print(f"[DEBUG] Found documents: {len(docs)}")
    
    user_db.close()
    return docs[0] if docs else None

def delete_document(doc_id, user_id):
    """Delete a specific document"""
    user_db = _get_user_db(user_id)
    documents_table = user_db.table('documents')
    Doc = Query()
    
    # Debug before deletion
    print(f"[DEBUG DELETE] Attempting to delete doc_id: {doc_id} (type: {type(doc_id)})")
    docs_before = len(documents_table.all())
    print(f"[DEBUG DELETE] Documents before deletion: {docs_before}")
    
    # Remove by doc_id field (string timestamp), not TinyDB's internal doc_id
    removed = documents_table.remove(Doc.doc_id == str(doc_id))
    
    docs_after = len(documents_table.all())
    print(f"[DEBUG DELETE] Documents after deletion: {docs_after}")
    print(f"[DEBUG DELETE] Removed count: {len(removed) if removed else 0}")
    
    user_db.close()
    return len(removed) > 0 if removed else False