import json
import os
import time
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from google import genai
from google.genai import types
from database import init_db, save_report, get_all_reports, get_report_by_id, delete_report

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max

# Initialize database
init_db()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing. Add it to the project-root .env file.")

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-3.8-flash"

ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

SYSTEM_PROMPT = """You are a helpful medical report assistant. You will receive a medical report as a PDF. Your job is to:
1. Summarize the medical report in simple language
2. Identify important test values
3. Flag values outside the reference ranges printed in the report (if the report gives no range, don't judge the value)
4. Explain medical terms in simple language

IMPORTANT: You are INFORMATIONAL ONLY. You must NOT diagnose diseases, prescribe medicines, or replace a doctor.
Always include a disclaimer that users should consult healthcare professionals.

Reply with JSON only (no markdown fences) using exactly these keys:
{
    "summary": "Simple summary of the report",
    "key_findings": ["Finding 1", "Finding 2"],
    "abnormal_values": ["Value 1 (reason)", "Value 2 (reason)"],
    "medical_terms_explained": {"term1": "simple explanation"},
    "disclaimer": "Medical disclaimer text"
}"""


def parse_json_reply(text):
    """Parse JSON from a reply, tolerating fences and surrounding text."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find('{'), text.rfind('}')
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                pass
    return None


def analyze_pdf(pdf_bytes):
    """Send the PDF directly to Gemini, including scanned documents."""
    try:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=MODEL,
                    contents=[
                        types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
                        "Please analyze this medical report. Reply with JSON only.",
                    ],
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        response_mime_type="application/json",
                        max_output_tokens=3000,
                    ),
                )
                break
            except Exception as e:
                unavailable = (
                    getattr(e, "code", None) == 503
                    or "503" in str(e)
                    or "UNAVAILABLE" in str(e).upper()
                )
                if not unavailable or attempt == 2:
                    raise
                time.sleep(2 ** attempt)

        reply = response.text or ""
        analysis = parse_json_reply(reply)
        if analysis is None:
            analysis = {
                "summary": reply,
                "key_findings": [],
                "abnormal_values": [],
                "medical_terms_explained": {},
                "disclaimer": "Please consult a healthcare professional for medical advice."
            }
        return analysis
    except Exception as e:
        if (
            getattr(e, "code", None) == 503
            or "503" in str(e)
            or "UNAVAILABLE" in str(e).upper()
        ):
            return {
                "error": "Gemini is temporarily busy. Please try analyzing the report again in a minute.",
                "disclaimer": "Please consult a healthcare professional for medical advice."
            }
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
            pdf_bytes = file.read()
            analysis = analyze_pdf(pdf_bytes)

            if 'error' in analysis:
                return jsonify({'error': analysis['error']}), 502

            report_id = save_report(
                filename=filename,
                extracted_text="",
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
def not_found(_error):
    return render_template('index.html'), 404

@app.errorhandler(413)
def too_large(_error):
    return jsonify({'error': 'File is too large (max 10 MB)'}), 413

@app.errorhandler(500)
def server_error(_error):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)