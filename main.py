
import os
import json
import re
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="EduGenie API",
    description="Google Gemini Powered Learning Assistant",
    version="1.0.0"
)


# -----------------------------
# REQUEST MODELS
# -----------------------------

class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=5000)


class TopicRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=500)


class TextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=20000)


# -----------------------------
# GEMINI AI CONFIGURATION
# -----------------------------

def generate_ai_response(prompt: str):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return None

    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=os.getenv(
                "GEMINI_MODEL",
                "gemini-2.5-flash"
            ),
            contents=prompt
        )

        return response.text

    except Exception as error:

        raise HTTPException(
            status_code=502,
            detail=f"Gemini API error: {str(error)}"
        )


def fallback_response(message):

    return (
        "Gemini API is not configured. "
        "Please add your GEMINI_API_KEY in the .env file. "
        "Your request was: " + message[:500]
    )


# -----------------------------
# HOME PAGE
# -----------------------------

@app.get("/")
def home():

    return FileResponse(
        BASE_DIR / "frontend" / "index.html"
    )


# -----------------------------
# HEALTH CHECK
# -----------------------------

@app.get("/api/health")
def health_check():

    return {
        "status": "success",
        "message": "EduGenie backend is running",
        "ai_configured": bool(
            os.getenv("GEMINI_API_KEY")
        )
    }


# -----------------------------
# MODULE 1: QUESTION ANSWERING
# -----------------------------

@app.post("/api/qa")
def question_answering(request: QuestionRequest):

    prompt = f"""
    You are EduGenie, an educational AI assistant.

    Answer the student's question in simple language.

    Include examples where useful.

    Question:
    {request.question}
    """

    result = generate_ai_response(prompt)

    if not result:
        result = fallback_response(request.question)

    return {
        "answer": result
    }


# -----------------------------
# MODULE 2: EXPLANATION
# -----------------------------

@app.post("/api/explain")
def explain_topic(request: TopicRequest):

    prompt = f"""
    Explain the following topic to a student.

    Topic: {request.topic}

    Include:

    1. Simple definition
    2. Detailed explanation
    3. Important points
    4. Real-world example
    5. Short summary

    Use easy English.
    """

    result = generate_ai_response(prompt)

    if not result:

        result = (
            f"Topic: {request.topic}\n\n"
            "Learn the basic definition first. "
            "Break the topic into smaller concepts. "
            "Study examples and practise applying what you learn. "
            "Configure Gemini API for a personalized explanation."
        )

    return {
        "explanation": result
    }


# -----------------------------
# MODULE 3: SUMMARIZATION
# -----------------------------

@app.post("/api/summarize")
def summarize_text(request: TextRequest):

    prompt = f"""
    Summarize the following educational text.

    Instructions:
    - Use simple English.
    - Preserve important information.
    - Use bullet points where appropriate.
    - Do not introduce unsupported facts.

    Text:
    {request.text}
    """

    result = generate_ai_response(prompt)

    if not result:

        words = request.text.split()

        result = " ".join(words[:70])

        if len(words) > 70:
            result += "..."

    return {
        "summary": result
    }


# -----------------------------
# MODULE 4: QUIZ GENERATION
# -----------------------------

@app.post("/api/quiz")
def generate_quiz(request: TopicRequest):

    prompt = f"""
    Create 5 multiple-choice questions about:

    {request.topic}

    Return ONLY a valid JSON array.

    Required format:

    [
      {{
        "question": "Question here",
        "options": [
          "Option A",
          "Option B",
          "Option C",
          "Option D"
        ],
        "answer": 0,
        "explanation": "Explanation here"
      }}
    ]

    The answer must be a zero-based index.
    """

    result = generate_ai_response(prompt)

    if result:

        try:

            match = re.search(
                r"\[.*\]",
                result,
                re.DOTALL
            )

            if not match:
                raise ValueError("Invalid JSON response")

            quiz_data = json.loads(match.group())

            if not isinstance(quiz_data, list):
                raise ValueError("Quiz must be a list")

            if not quiz_data:
                raise ValueError("Empty quiz")

            for question in quiz_data:

                if not isinstance(question.get("question"), str):
                    raise ValueError("Invalid question")

                options = question.get("options")

                if not isinstance(options, list) or len(options) != 4:
                    raise ValueError("Invalid options")

                answer = question.get("answer")

                if not isinstance(answer, int) or not 0 <= answer < 4:
                    raise ValueError("Invalid answer index")

            return {
                "quiz": quiz_data
            }

        except (ValueError, TypeError, json.JSONDecodeError):
            pass

    return {
        "quiz": [
            {
                "question": f"What is an important first step when learning {request.topic}?",
                "options": [
                    "Understand the basic concepts",
                    "Memorize without context",
                    "Skip all examples",
                    "Avoid practice"
                ],
                "answer": 0,
                "explanation": "Understanding the foundation makes learning easier."
            }
        ]
    }


# -----------------------------
# MODULE 5: LEARNING PATH
# -----------------------------

@app.get("/api/learn/recommendations")
def learning_recommendations(topic: str):

    if not topic.strip():
        raise HTTPException(
            status_code=400,
            detail="Topic cannot be empty"
        )

    prompt = f"""
    Create a structured learning roadmap for:

    {topic}

    Include:

    1. Beginner level
    2. Intermediate level
    3. Advanced level
    4. Practice activities
    5. Recommended learning order
    6. Revision tips

    Explain using simple language.
    """

    result = generate_ai_response(prompt)

    if not result:

        result = f"""
        Learning Roadmap: {topic}

        1. Beginner:
        Learn definitions and fundamentals.

        2. Intermediate:
        Understand important concepts and examples.

        3. Advanced:
        Study advanced applications.

        4. Practice:
        Solve exercises and create small projects.

        5. Revision:
        Review important concepts regularly.

        Configure Gemini API for AI-generated recommendations.
        """

    return {
        "topic": topic,
        "recommendation": result
    }


# -----------------------------
# FRONTEND STATIC FILES
# -----------------------------

app.mount(
    "/static",
    StaticFiles(
        directory=BASE_DIR / "frontend"
    ),
    name="static"
)