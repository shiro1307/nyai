from flask import render_template, request, redirect, url_for, session, flash
from auth import login_required
import database
import ai_service

def register_main_routes(app):
    @app.route('/')
    @login_required
    def home():
        return render_template('home.html', answer=None)

    @app.route('/ask', methods=['POST'])
    @login_required
    def ask():
        question = request.form.get('question')
        prompt = f"Legal Question: {question}\n\nProvide a helpful legal answer."
        answer = ai_service.call_ai_api(prompt)
        database.save_document(session['user_id'], 'Q&A', question, answer)
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
            analysis = ai_service.call_ai_api(prompt)
            database.save_document(session['user_id'], 'Contract Review', contract_text, analysis)
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
            
            letter = ai_service.call_ai_api(prompt)
            input_text = f"From: {sender}\nTo: {recipient}\nIssue: {issue}"
            database.save_document(session['user_id'], 'Demand Letter', input_text, letter)
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
            analysis = ai_service.call_ai_api(prompt)
            database.save_document(session['user_id'], 'Document Analysis', document_text, analysis)
            return render_template('document_analysis.html', analysis=analysis)
        return render_template('document_analysis.html', analysis=None)

    @app.route('/history')
    @login_required
    def history():
        user_docs = database.get_user_documents(session['user_id'])
        return render_template('history.html', documents=user_docs)

    @app.route('/view/<doc_id>')
    @login_required
    def view_document(doc_id):
        print(f"[ROUTE DEBUG] Received doc_id: {doc_id}")
        print(f"[ROUTE DEBUG] Session user_id: {session.get('user_id')}")
        
        document = database.get_document(doc_id, session['user_id'])
        if document:
            return render_template('view_document.html', document=document)
        else:
            flash('Document not found')
            return redirect(url_for('history'))

    @app.route('/delete/<doc_id>')
    @login_required
    def delete_document(doc_id):
        print(f"[ROUTE DEBUG] Deleting doc_id: {doc_id}")
        success = database.delete_document(doc_id, session['user_id'])
        if success:
            flash('Document deleted successfully')
        else:
            flash('Document not found or already deleted')
        return redirect(url_for('history'))