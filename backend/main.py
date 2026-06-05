import os
import shutil
from typing import List

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from quiz_llm import QuizCrafter

app = FastAPI()

# CORS setup to allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load QuizCrafter
ques_llm = QuizCrafter()

# Directory for uploaded PDFs
UPLOAD_FOLDER = "./uploads"


class Answer(BaseModel):
    text: str
    correct: bool


class QuestionResponse(BaseModel):
    question: str
    answers: List[Answer]


def format_questions(questions):
    formatted_questions = []

    for question_obj in questions:
        # अगर AI से रिस्पॉन्स खाली या गलत फॉर्मेट में आए तो क्रैश होने से बचाए
        if not question_obj or "question" not in question_obj or "options" not in question_obj:
            continue
            
        formatted_question = {
            "question": question_obj["question"],
            "answers": [
                {
                    "text": option,
                    "correct": option.startswith(
                        question_obj.get("correct_answer", "")
                    ),
                }
                for option in question_obj["options"]
            ],
        }

        formatted_questions.append(
            QuestionResponse(**formatted_question)
        )

    return formatted_questions


@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        file_path = os.path.join(
            UPLOAD_FOLDER,
            "book.pdf"
        )

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        return {
            "message": "File uploaded successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post(
    "/generate-questions/",
    response_model=List[QuestionResponse]
)
async def generate_questions(
    topic: str = Form(...),
    num_questions: int = Form(5)  # <-- यहाँ नया पैरामीटर जोड़ा, डिफ़ॉल्ट 5 रहेगा
):
    try:
        pdf_path = os.path.join(
            UPLOAD_FOLDER,
            "book.pdf"
        )

        if not os.path.exists(pdf_path):
            raise HTTPException(
                status_code=400,
                detail="कृपया पहले PDF फाइल अपलोड करें।"
            )

        ques_llm.load_docs(pdf_path)

        # यहाँ हम topic के साथ सवालों की संख्या भी भेज रहे हैं
        questions = ques_llm.get_questions(topic, num_questions)

        formatted_questions = format_questions(
            questions
        )

        return formatted_questions

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
