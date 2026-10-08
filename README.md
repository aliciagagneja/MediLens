# MediLens

**AI-Powered Medical Report Assistant**

MediLens helps users understand medical reports by extracting text, analyzing it with AI, and presenting complex medical information in simple, easy-to-understand language.

> **Medical Disclaimer:** MediLens is an informational tool only. It does NOT diagnose diseases, prescribe medicines, or replace professional medical advice. Always consult a qualified healthcare professional for medical decisions.

---

## Features (Current)

✅ **Upload Medical Reports** - Upload PDF medical reports  
✅ **AI-Powered Analysis** - Claude AI analyzes reports and explains findings  
✅ **Simple Explanations** - Medical terminology explained in plain language  
✅ **Save Reports** - Store reports locally and access them anytime  
✅ **View History** - See all your uploaded reports with dates  
✅ **Delete Reports** - Remove reports you no longer need  
✅ **Professional Design** - Clean, modern, responsive website  

## Features (Coming Soon)

🔄 **Compare Reports** - Compare two reports from different dates to track changes  
📊 **Advanced Analytics** - Visual comparisons of values over time  

---

## Tech Stack

- **Backend:** Python + Flask
- **Frontend:** HTML + CSS + JavaScript
- **Database:** SQLite
- **PDF Processing:** PyMuPDF (fitz)
- **AI:** Anthropic Claude API
- **Deployment:** Flask dev server (local) / Can scale with Gunicorn

---

## Setup & Installation

### Requirements
- Python 3.8+
- pip (Python package manager)
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/aliciagagneja/MediLens.git
cd MediLens
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
```

Activate it:
- **Windows:**
  ```bash
  venv\Scripts\activate
  ```
- **Mac/Linux:**
  ```bash
  source venv/bin/activate
  ```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up API Key

1. Get your API key from [Anthropic Console](https://console.anthropic.com)
2. Create a `.env` file in the project root:
   ```
   ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE
   ```
3. Replace `YOUR_KEY_HERE` with your actual key

### Step 5: Run the App

```bash
python app.py
```

You should see:
```
Running on http://127.0.0.1:5000
```

Open your browser and go to: **http://localhost:5000**

---

## How It Works

1. **Upload** → User uploads a medical report (PDF format)
2. **Extract** → App extracts text from the PDF using PyMuPDF
3. **Analyze** → Text is sent to Claude AI for analysis
4. **Display** → AI-generated summary, key findings, and explanations shown
5. **Save** → Report is stored in local SQLite database
6. **Access** → User can view saved reports anytime

### User Flow

```
Home Page → Upload Report → AI Analysis → Results Page → View Saved Reports
```

---

## File Structure

```
MediLens/
├── app.py                 # Flask main server & routes
├── database.py            # SQLite database functions
├── requirements.txt       # Python dependencies
├── .env                   # API keys (not in git)
├── .gitignore            # Excludes venv, .db, uploads, .env
├── static/
│   ├── css/style.css     # All styling (responsive, clean design)
│   └── js/script.js      # Form handling, drag-drop, interactions
├── templates/
│   ├── base.html         # Base layout (navbar, footer)
│   ├── index.html        # Home page
│   ├── upload.html       # Upload form
│   ├── results.html      # Analysis results display
│   └── saved.html        # List saved reports
├── uploads/              # Temporary PDF storage
└── medilens.db          # SQLite database (auto-created)
```

---

## API & Database

### Claude API Integration

The app uses Claude 3.5 Sonnet to analyze medical reports. The system prompt instructs Claude to:
- Summarize the report in simple language
- Identify important test values
- Flag values outside normal ranges
- Explain medical terms clearly
- Always include a disclaimer

### Database Schema

**Table: `reports`**
| Column | Type | Purpose |
|--------|------|---------|
| id | INTEGER (PK) | Unique identifier |
| filename | TEXT | Original PDF filename |
| upload_date | TIMESTAMP | When report was uploaded |
| extracted_text | TEXT | Raw text from PDF |
| summary | TEXT | AI summary |
| key_findings | TEXT | JSON list of findings |
| analysis_data | TEXT | Full JSON response from Claude |

---

## Current Limitations

- ❌ No user authentication (all reports are in one shared database)
- ❌ PDF extraction only works on text-based PDFs (not scanned/image-heavy PDFs)
- ❌ Compare reports feature not yet implemented
- ❌ No email/export functionality
- ⚠️ Requires valid Anthropic API key with available credits

---

## Troubleshooting

### "No summary available" after upload
**Issue:** API key is invalid or not set  
**Fix:** Check `.env` file has correct `ANTHROPIC_API_KEY`, then refresh page

### "Error extracting PDF"
**Issue:** PDF is image-based (scanned document)  
**Fix:** Try a different PDF with searchable text

### "Error uploading file"
**Issue:** File type is not PDF  
**Fix:** Make sure you're uploading a `.pdf` file

### Virtual environment not activating
**Windows:**
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\activate
```

---

## Development

### Adding Features
1. Edit routes in `app.py`
2. Create new templates in `templates/`
3. Add styling to `static/css/style.css`
4. Add interactivity to `static/js/script.js`
5. Test locally before pushing

### Making Database Changes
Edit `database.py` → Delete `medilens.db` → Restart app (new DB created)

### Deploying to Production
Use Gunicorn instead of Flask dev server:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## Security Notes

⚠️ **This is a development project. Before deploying publicly:**

- [ ] Add user authentication
- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS
- [ ] Add rate limiting
- [ ] Sanitize file uploads
- [ ] Use a production database (PostgreSQL, not SQLite)
- [ ] Add logging & monitoring
- [ ] Implement CORS policies

---

## Team

**Alicia** - Student, VIT Vellore  
**+ 1 team member** - Python assignment project

---

## License

This project is created for educational purposes as part of a Python assignment.

---

## Support

For issues, questions, or feature requests:
1. Check this README
2. Check `MEDILENS_HANDOFF.md` for technical details
3. Open an issue on GitHub

---

## Next Steps (Roadmap)

- [ ] Implement compare reports feature
- [ ] Add PDF export for results
- [ ] Improve error messages
- [ ] Add user authentication
- [ ] Support for more file formats (DOCX, TXT)
- [ ] API endpoint for programmatic access
- [ ] Mobile app (React Native)

---

**Made with ❤️ for better healthcare understanding**
