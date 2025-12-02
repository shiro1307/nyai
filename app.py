from flask import Flask, render_template, request, redirect, url_for, session, flash
from tinydb import TinyDB, Query
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Database setup
db = TinyDB('legal_assistant.json')
users_table = db.table('users')
documents_table = db.table('documents')

# ==================== AI FUNCTION (YOU IMPLEMENT API CALL HERE) ====================
def call_ai_api(prompt):
    """
    Replace this function body with your LLM API call
    Arguments: prompt (string) - the input prompt
    Returns: string - AI response
    """
    # TODO: Add your API call here
    # Example:
    # response = your_api_client.generate(prompt)
    # return response
    
    return f"[AI Response Placeholder]\n\nYou sent: {prompt}\n\nReplace call_ai_api() function in app.py with your actual LLM API call."

# ==================== HELPER FUNCTIONS ====================

def login_required(f):
    """Decorator to require login"""
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

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

# ==================== ROUTES ====================

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        
        if password != confirm:
            flash('Passwords do not match')
            return render_template('signup.html')
        
        User = Query()
        if users_table.search(User.username == username):
            flash('Username already exists')
            return render_template('signup.html')
        
        users_table.insert({
            'username': username,
            'password': generate_password_hash(password)
        })
        
        flash('Account created! Please login.')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        User = Query()
        user = users_table.search(User.username == username)
        
        if user and check_password_hash(user[0]['password'], password):
            session['user_id'] = user[0].doc_id
            session['username'] = username
            flash('Login successful!')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully')
    return redirect(url_for('login'))

@app.route('/', methods=['GET'])
@login_required
def home():
    return render_template('home.html', answer=None)

@app.route('/ask', methods=['POST'])
@login_required
def ask():
    question = request.form.get('question')
    
    prompt = f"Legal Question: {question}\n\nProvide a helpful legal answer."
    answer = call_ai_api(prompt)
    
    save_document(session['user_id'], 'Q&A', question, answer)
    
    return render_template('home.html', answer=answer)

@app.route('/contract_review', methods=['GET', 'POST'])
@login_required
def contract_review():
    if request.method == 'POST':
        contract_text = request.form.get('contract_text')
        
        prompt = f"""Analyze this contract and provide:
1. Key clauses and their implications
2. Risk flags (high/medium/low risk items)
3. Missing standard clauses
4. Overall assessment

Contract:
{contract_text}"""
        
        analysis = call_ai_api(prompt)
        save_document(session['user_id'], 'Contract Review', contract_text, analysis)
        
        return render_template('contract_review.html', analysis=analysis)
    
    return render_template('contract_review.html', analysis=None)

@app.route('/demand_letter', methods=['GET', 'POST'])
@login_required
def demand_letter():
    if request.method == 'POST':
        sender = request.form.get('sender_name')
        recipient = request.form.get('recipient_name')
        issue = request.form.get('issue')
        demand = request.form.get('demand')
        deadline = request.form.get('deadline')
        
        prompt = f"""Generate a professional demand letter:

From: {sender}
To: {recipient}
Issue: {issue}
Demand: {demand}
Deadline: {deadline}

Create a formal, legally sound demand letter."""
        
        letter = call_ai_api(prompt)
        input_text = f"From: {sender}\nTo: {recipient}\nIssue: {issue}"
        save_document(session['user_id'], 'Demand Letter', input_text, letter)
        
        return render_template('demand_letter.html', letter=letter)
    
    return render_template('demand_letter.html', letter=None)

@app.route('/document_analysis', methods=['GET', 'POST'])
@login_required
def document_analysis():
    if request.method == 'POST':
        document_text = request.form.get('document_text')
        
        prompt = f"""Analyze this legal document and extract:
1. All important clauses
2. Risk levels for each clause
3. Missing elements
4. Recommendations

Document:
{document_text}"""
        
        analysis = call_ai_api(prompt)
        save_document(session['user_id'], 'Document Analysis', document_text, analysis)
        
        return render_template('document_analysis.html', analysis=analysis)
    
    return render_template('document_analysis.html', analysis=None)

@app.route('/history')
@login_required
def history():
    Doc = Query()
    user_docs = documents_table.search(Doc.user_id == session['user_id'])
    return render_template('history.html', documents=user_docs)

@app.route('/view/<doc_id>')
@login_required
def view_document(doc_id):
    Doc = Query()
    document = documents_table.search(
        (Doc.doc_id == doc_id) & (Doc.user_id == session['user_id'])
    )
    
    if document:
        return render_template('view_document.html', document=document[0])
    else:
        flash('Document not found')
        return redirect(url_for('history'))

@app.route('/delete/<doc_id>')
@login_required
def delete_document(doc_id):
    Doc = Query()
    documents_table.remove(
        (Doc.doc_id == doc_id) & (Doc.user_id == session['user_id'])
    )
    flash('Document deleted')
    return redirect(url_for('history'))

# ==================== RUN APP ====================

if __name__ == '__main__':
    app.run(debug=True, port=5000)