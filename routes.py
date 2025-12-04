from flask import render_template, request, redirect, url_for, session, flash
from auth import login_required
import database
import ai_service
# Add these imports at the top of the file (around line 1-3)
from flask import render_template, request, redirect, url_for, session, flash, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import io
from flask import render_template, request, redirect, url_for, session, flash, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import io
import re

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

    # Add this new route after the document_analysis route (around line 60)

    @app.route('/compare', methods=['GET', 'POST'])
    @login_required
    def compare_documents():
        if request.method == 'POST':
            doc1 = request.form.get('document1')
            doc2 = request.form.get('document2')
            
            prompt = f"""Compare these two documents and provide a detailed analysis:

    1. KEY DIFFERENCES: List the major differences in terms, clauses, and conditions
    2. FAVORABLE ANALYSIS: Which document is more favorable and why?
    3. MISSING CLAUSES: What clauses are in one but not the other?
    4. RISK COMPARISON: Compare risk levels between both documents
    5. RECOMMENDATIONS: What actions should be taken?

    Document 1:
    {doc1}

    Document 2:
    {doc2}"""
            
            comparison = ai_service.call_ai_api(prompt)
            database.save_document(session['user_id'], 'Document Comparison', f"Comparison Analysis", comparison)
            return render_template('compare.html', comparison=comparison)
        
        return render_template('compare.html', comparison=None)

    # Add this route at the very end of the register_main_routes function, before the last line

    @app.route('/export/<doc_id>')
    @login_required
    def export_pdf(doc_id):
        """Export document as PDF with Markdown formatting"""
        document = database.get_document(doc_id, session['user_id'])
        
        if not document:
            flash('Document not found')
            return redirect(url_for('history'))
        
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, 
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles for better formatting
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_LEFT, TA_CENTER
        
        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor='navy',
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Heading style
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor='#2c3e50',
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Body style
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            spaceAfter=10
        )
        
        # Title
        title = Paragraph(f"<b>{document['type']}</b>", title_style)
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Metadata box
        date_text = Paragraph(f"<b>Date:</b> {document['date']}", body_style)
        story.append(date_text)
        
        # Risk Score if available
        if document.get('risk_score') is not None:
            risk_score = document['risk_score']
            if risk_score <= 30:
                risk_color = '#28a745'
                risk_level = 'Low Risk'
            elif risk_score <= 60:
                risk_color = '#ffc107'
                risk_level = 'Medium Risk'
            else:
                risk_color = '#dc3545'
                risk_level = 'High Risk'
            
            risk_text = f'<b>Risk Score:</b> <font color="{risk_color}"><b>{risk_score}/100 - {risk_level}</b></font>'
            risk_para = Paragraph(risk_text, body_style)
            story.append(risk_para)
        
        story.append(Spacer(1, 0.3*inch))
        
        # Input section
        input_heading = Paragraph("<b>Input Document:</b>", heading_style)
        story.append(input_heading)
        
        # Process input with markdown
        input_formatted = format_markdown_for_pdf(document['input'], body_style)
        for para in input_formatted:
            story.append(para)
        
        story.append(Spacer(1, 0.3*inch))
        
        # Output section
        output_heading = Paragraph("<b>Analysis Output:</b>", heading_style)
        story.append(output_heading)
        
        # Process output with markdown
        output_formatted = format_markdown_for_pdf(document['output'], body_style)
        for para in output_formatted:
            story.append(para)
        
        # Build PDF
        try:
            doc.build(story)
            buffer.seek(0)
            
            # Send file
            filename = f"{document['type'].replace(' ', '_')}_{doc_id}.pdf"
            return send_file(
                buffer,
                download_name=filename,
                as_attachment=True,
                mimetype='application/pdf'
            )
        except Exception as e:
            flash(f'Error generating PDF: {str(e)}')
            return redirect(url_for('view_document', doc_id=doc_id))


    def format_markdown_for_pdf(text, base_style):
        """
        Convert markdown-like formatting to PDF paragraphs
        Handles: **bold**, *italic*, headers, bullet points, numbered lists
        """
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import inch
        import re
        
        paragraphs = []
        lines = text.split('\n')
        
        # Style for headers
        h1_style = ParagraphStyle(
            'H1',
            parent=base_style,
            fontSize=14,
            textColor='#2c3e50',
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )
        
        h2_style = ParagraphStyle(
            'H2',
            parent=base_style,
            fontSize=12,
            textColor='#34495e',
            spaceAfter=8,
            spaceBefore=8,
            fontName='Helvetica-Bold'
        )
        
        h3_style = ParagraphStyle(
            'H3',
            parent=base_style,
            fontSize=11,
            textColor='#34495e',
            spaceAfter=6,
            spaceBefore=6,
            fontName='Helvetica-Bold'
        )
        
        # Bullet and numbered list styles
        bullet_style = ParagraphStyle(
            'Bullet',
            parent=base_style,
            leftIndent=20,
            bulletIndent=10,
            spaceAfter=4
        )
        
        for line in lines:
            line = line.strip()
            
            if not line:
                paragraphs.append(Spacer(1, 0.1*inch))
                continue
            
            # Escape special XML characters first
            line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            # Convert markdown to HTML-like tags for ReportLab
            # Headers
            if line.startswith('### '):
                content = line[4:]
                content = apply_inline_formatting(content)
                paragraphs.append(Paragraph(content, h3_style))
            elif line.startswith('## '):
                content = line[3:]
                content = apply_inline_formatting(content)
                paragraphs.append(Paragraph(content, h2_style))
            elif line.startswith('# '):
                content = line[2:]
                content = apply_inline_formatting(content)
                paragraphs.append(Paragraph(content, h1_style))
            
            # Bullet points
            elif line.startswith('- ') or line.startswith('* '):
                content = line[2:]
                content = apply_inline_formatting(content)
                paragraphs.append(Paragraph(f'• {content}', bullet_style))
            
            # Numbered lists
            elif re.match(r'^\d+\.\s', line):
                content = re.sub(r'^\d+\.\s', '', line)
                content = apply_inline_formatting(content)
                number = re.match(r'^(\d+)\.', line).group(1)
                paragraphs.append(Paragraph(f'{number}. {content}', bullet_style))
            
            # Regular paragraphs
            else:
                content = apply_inline_formatting(line)
                # Limit very long paragraphs
                if len(content) > 3000:
                    content = content[:3000] + '...'
                try:
                    paragraphs.append(Paragraph(content, base_style))
                except:
                    # Fallback for problematic content
                    safe_content = ''.join(c if ord(c) < 128 else ' ' for c in content)
                    paragraphs.append(Paragraph(safe_content, base_style))
        
        return paragraphs


    def apply_inline_formatting(text):
        """
        Apply inline markdown formatting: **bold**, *italic*, `code`
        """
        # Bold: **text** -> <b>text</b>
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        
        # Italic: *text* -> <i>text</i>
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        
        # Code: `text` -> <font face="Courier">text</font>
        text = re.sub(r'`(.+?)`', r'<font face="Courier" color="#c7254e">\1</font>', text)
        
        return text