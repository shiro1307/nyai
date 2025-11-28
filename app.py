# AI Legal Assistant - Single File Flask App
# Simple version with TinyDB, no CSS, login/signup included

from flask import Flask, render_template_string, request, redirect, url_for, session, flash
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

# ==================== TEMPLATES ====================

BASE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Legal Assistant</title>
</head>
<body>
    <h1>AI Legal Assistant</h1>
    {% if session.get('user_id') %}
        <p>Welcome, {{ session.get('username') }}! | <a href="/logout">Logout</a></p>
        <hr>
        <a href="/">Home</a> | 
        <a href="/contract_review">Contract Review</a> | 
        <a href="/demand_letter">Demand Letter</a> | 
        <a href="/document_analysis">Document Analysis</a> |
        <a href="/history">History</a>
        <hr>
    {% endif %}
    
    {% with messages = get_flashed_messages() %}
        {% if messages %}
            {% for message in messages %}
                <p><strong>{{ message }}</strong></p>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    {% block content %}{% endblock %}
</body>
</html>
"""

LOGIN_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', """
{% block content %}
    <h2>Login</h2>
    <form method="POST">
        <p>Username: <input type="text" name="username" required></p>
        <p>Password: <input type="password" name="password" required></p>
        <button type="submit">Login</button>
    </form>
    <p>Don't have an account? <a href="/signup">Sign Up</a></p>
{% endblock %}
""")

SIGNUP_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', """
{% block content %}
    <h2>Sign Up</h2>
    <form method="POST">
        <p>Username: <input type="text" name="username" required></p>
        <p>Password: <input type="password" name="password" required></p>
        <p>Confirm Password: <input type="password" name="confirm_password" required></p>
        <button type="submit">Sign Up</button>
    </form>
    <p>Already have an account? <a href="/login">Login</a></p>
{% endblock %}
""")

HOME_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', """
{% block content %}
    <h2>Welcome to AI Legal Assistant</h2>
    <p>This platform helps you with legal tasks using AI.</p>
    
    <h3>Features:</h3>
    <ul>
        <li>Contract Review - Analyze contracts for risks</li>
        <li>Demand Letter Generator - Create professional demand letters</li>
        <li>Document Analysis - Extract clauses and identify issues</li>
        <li>Legal Q&A - Ask legal questions</li>
    </ul>
    
    <h3>Ask a Legal Question</h3>
    <form method="POST" action="/ask">
        <p><textarea name="question" rows="5" cols="60" placeholder="Enter your legal question..." required></textarea></p>
        <button type="submit">Ask AI</button>
    </form>
    
    {% if answer %}
        <hr>
        <h3>Answer:</h3>
        <pre>{{ answer }}</pre>
    {% endif %}
{% endblock %}
""")

CONTRACT_REVIEW_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', """
{% block content %}
    <h2>Contract Review</h2>
    <p>Paste your contract text below for automated analysis.</p>
    
    <form method="POST">
        <p><textarea name="contract_text" rows="15" cols="80" placeholder="Paste contract text here..." required></textarea></p>
        <button type="submit">Analyze Contract</button>
    </form>
    
    {% if analysis %}
        <hr>
        <h3>Analysis:</h3>
        <pre>{{ analysis }}</pre>
    {% endif %}
    
    <hr>
    <h3>Review Checklist:</h3>
    <ul>
        <li>Review all identified clauses</li>
        <li>Address high-risk items</li>
        <li>Check for missing standard clauses</li>
        <li>Consult attorney for concerns</li>
    </ul>
{% endblock %}
""")

DEMAND_LETTER_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', """
{% block content %}
    <h2>Demand Letter Generator</h2>
    
    <form method="POST">
        <p>Your Name: <input type="text" name="sender_name" size="50" required></p>
        <p>Recipient Name: <input type="text" name="recipient_name" size="50" required></p>
        <p>Issue Description:</p>
        <p><textarea name="issue" rows="5" cols="60" required></textarea></p>
        <p>Your Demand:</p>
        <p><textarea name="demand" rows="3" cols="60" required></textarea></p>
        <p>Deadline: <input type="text" name="deadline" value="14 days" size="20"></p>
        <button type="submit">Generate Letter</button>
    </form>
    
    {% if letter %}
        <hr>
        <h3>Generated Demand Letter:</h3>
        <pre>{{ letter }}</pre>
    {% endif %}
{% endblock %}
""")

DOCUMENT_ANALYSIS_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', """
{% block content %}
    <h2>Document Analysis</h2>
    <p>Extract clauses and identify risks in legal documents.</p>
    
    <form method="POST">
        <p><textarea name="document_text" rows="15" cols="80" placeholder="Paste document text here..." required></textarea></p>
        <button type="submit">Analyze Document</button>
    </form>
    
    {% if analysis %}
        <hr>
        <h3>Analysis:</h3>
        <pre>{{ analysis }}</pre>
    {% endif %}
{% endblock %}
""")

HISTORY_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', """
{% block content %}
    <h2>Your Document History</h2>
    
    {% if documents %}
        <table border="1" cellpadding="5">
            <tr>
                <th>Type</th>
                <th>Date</th>
                <th>Preview</th>
                <th>Action</th>
            </tr>
            {% for doc in documents %}
            <tr>
                <td>{{ doc.type }}</td>
                <td>{{ doc.date }}</td>
                <td>{{ doc.preview }}</td>
                <td><a href="/view/{{ doc.doc_id }}">View</a> | <a href="/delete/{{ doc.doc_id }}">Delete</a></td>
            </tr>
            {% endfor %}
        </table>
    {% else %}
        <p>No documents yet. Start using the tools above!</p>
    {% endif %}
{% endblock %}
""")

VIEW_DOCUMENT_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', """
{% block content %}
    <h2>Document Details</h2>
    
    {% if document %}
        <p><strong>Type:</strong> {{ document.type }}</p>
        <p><strong>Date:</strong> {{ document.date }}</p>
        <hr>
        <h3>Input:</h3>
        <pre>{{ document.input }}</pre>
        <hr>
        <h3>Output:</h3>
        <pre>{{ document.output }}</pre>
        <hr>
        <a href="/history">Back to History</a>
    {% else %}
        <p>Document not found.</p>
    {% endif %}
{% endblock %}
""")

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
            return render_template_string(SIGNUP_TEMPLATE)
        
        User = Query()
        if users_table.search(User.username == username):
            flash('Username already exists')
            return render_template_string(SIGNUP_TEMPLATE)
        
        users_table.insert({
            'username': username,
            'password': generate_password_hash(password)
        })
        
        flash('Account created! Please login.')
        return redirect(url_for('login'))
    
    return render_template_string(SIGNUP_TEMPLATE)

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
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully')
    return redirect(url_for('login'))

@app.route('/', methods=['GET'])
@login_required
def home():
    return render_template_string(HOME_TEMPLATE, answer=None)

@app.route('/ask', methods=['POST'])
@login_required
def ask():
    question = request.form.get('question')
    
    prompt = f"Legal Question: {question}\n\nProvide a helpful legal answer."
    answer = call_ai_api(prompt)
    
    save_document(session['user_id'], 'Q&A', question, answer)
    
    return render_template_string(HOME_TEMPLATE, answer=answer)

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
        
        return render_template_string(CONTRACT_REVIEW_TEMPLATE, analysis=analysis)
    
    return render_template_string(CONTRACT_REVIEW_TEMPLATE, analysis=None)

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
        
        return render_template_string(DEMAND_LETTER_TEMPLATE, letter=letter)
    
    return render_template_string(DEMAND_LETTER_TEMPLATE, letter=None)

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
        
        return render_template_string(DOCUMENT_ANALYSIS_TEMPLATE, analysis=analysis)
    
    return render_template_string(DOCUMENT_ANALYSIS_TEMPLATE, analysis=None)

@app.route('/history')
@login_required
def history():
    Doc = Query()
    user_docs = documents_table.search(Doc.user_id == session['user_id'])
    return render_template_string(HISTORY_TEMPLATE, documents=user_docs)

@app.route('/view/<doc_id>')
@login_required
def view_document(doc_id):
    Doc = Query()
    document = documents_table.search(
        (Doc.doc_id == doc_id) & (Doc.user_id == session['user_id'])
    )
    
    if document:
        return render_template_string(VIEW_DOCUMENT_TEMPLATE, document=document[0])
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


# ==================== REQUIREMENTS.TXT ====================
"""
Create a file called requirements.txt with:

Flask==3.0.0
tinydb==4.8.0
"""

# ==================== SETUP INSTRUCTIONS ====================
"""
1. Save this code as app.py

2. Create requirements.txt with:
   Flask==3.0.0
   tinydb==4.8.0

3. Install dependencies:
   pip install -r requirements.txt

4. Replace the call_ai_api() function (line 20) with your actual LLM API call

5. Run:
   python app.py

6. Visit: http://localhost:5000

7. Sign up and start using!

Note: A file called legal_assistant.json will be created automatically for the database.
"""