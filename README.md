
# EduGenie
## Google Gemini Powered Learning Assistant

EduGenie is an AI-powered educational application.

### Features

1. AI Question Answering
2. Topic Explanation
3. Text Summarization
4. AI Quiz Generation
5. Personalized Learning Path

### Technologies

Frontend:
- HTML
- CSS
- JavaScript

Backend:
- Python
- FastAPI

AI:
- Google Gemini API

### Installation

Create virtual environment:

python -m venv .venv

Activate environment:

Windows:
.venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

### Run Application

python -m uvicorn app.main:app --reload

### Application URL

http://127.0.0.1:8000

### API Documentation

http://127.0.0.1:8000/docs

### Health Check

http://127.0.0.1:8000/api/health