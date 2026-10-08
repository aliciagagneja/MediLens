import os
import fitz
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from anthropic import Anthropic
from database import init_db, save_report, get_all_reports, get_report_by_id, delete_report

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
init_db()

# Anthropic client
client = Anthropic()

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_pdf_text(pdf_path):
    """Extract text from PDF using PyMuPDF"""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"

def analyze_with_claude(text):
    """Use Claude API to analyze medical report"""
    try:
        # System prompt for medical analysis
        system_prompt = """You are a helpful medical report assistant. Your job is to:
1. Summarize the medical report in simple language
2. Identify important test values
3. Flag values outside normal ranges (if mentioned)
4. Explain medical terms in simple language

IMPORTANT: You are INFORMATIONAL ONLY. You must NOT diagnose diseases, prescribe medicines, or replace a doctor.
Always include a disclaimer that users should consult healthcare professionals.

Format your response as JSON with these exact keys:
{
    "summary": "Simple summary of the report",
    "key_findings": ["Finding 1", "Finding 2", ...],
    "abnormal_values": ["Value 1 (reason)", "Value 2 (reason)", ...],
    "medical_terms_explained": {"term1": "simple explanation", "term2": "explanation"},
    "disclaimer": "Medical disclaimer text"
}"""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {"role": "user", "content": f"Please analyze this medical report:\n\n{text}"}
            ]
        )
        
        # Extract response text
        response_text = message.content[0].text
        
        # Try to parse as JSON
        try:
            analysis = json.loads(response_text)
        except json.JSONDecodeError:
            # If not valid JSON, wrap it
            analysis = {
                "summary": response_text,
                "key_findings": [],
                "abnormal_values": [],
                "medical_terms_explained": {},
                "disclaimer": "Please consult a healthcare professional for medical advice."
            }
        
        return analysis
    except Exception as e:
        return {
            "error": f"Error analyzing report: {str(e)}",
            "disclaimer": "Please consult a healthcare professional for medical advice."
        }

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Upload medical report"""
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Extract text from PDF
            extracted_text = extract_pdf_text(filepath)
            
            # Analyze with Claude
            analysis = analyze_with_claude(extracted_text)
            
            # Save to database
            report_id = save_report(
                filename=filename,
                extracted_text=extracted_text,
                summary=analysis.get('summary', ''),
                key_findings=json.dumps(analysis.get('key_findings', [])),
                analysis_data=analysis
            )
            
            return jsonify({
                'success': True,
                'report_id': report_id,
                'filename': filename,
                'analysis': analysis
            })
        
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    
    return render_template('upload.html')

@app.route('/api/analysis/<int:report_id>')
def get_analysis(report_id):
    """Get analysis for a specific report"""
    report = get_report_by_id(report_id)
    
    if not report:
        return jsonify({'error': 'Report not found'}), 404
    
    return jsonify({
        'id': report[0],
        'filename': report[1],
        'upload_date': report[2],
        'summary': report[4],
        'key_findings': json.loads(report[5]) if report[5] else [],
        'analysis': json.loads(report[6]) if report[6] else {}
    })

@app.route('/saved')
def saved_reports():
    """View all saved reports"""
    reports = get_all_reports()
    return render_template('saved.html', reports=reports)

@app.route('/results/<int:report_id>')
def results(report_id):
    """Display analysis results for a report"""
    report = get_report_by_id(report_id)
    
    if not report:
        return redirect(url_for('index'))
    
    analysis = json.loads(report[6]) if report[6] else {}
    
    return render_template('results.html', 
                         report_id=report_id,
                         filename=report[1],
                         analysis=analysis)

@app.route('/delete/<int:report_id>', methods=['POST'])
def delete(report_id):
    """Delete a report"""
    try:
        delete_report(report_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)