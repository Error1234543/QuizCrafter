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

    if not isinstance(questions, list):
        print(f"Backend Error: AI did not return a list. Type received: {type(questions)}")
        return formatted_questions

    for question_obj in questions:
        # સુરક્ષા ચેક: જો ડેટા અધૂરો હોય તો સ્કીપ કરો
        if not isinstance(question_obj, dict) or "question" not in question_obj or "options" not in question_obj:
            continue
            
        options = question_obj["options"]
        if not isinstance(options, list):
            continue

        correct_ans = str(question_obj.get("correct_answer", "")).strip()

        answers_list = []
        for option in options:
            opt_str = str(option).strip()
            # ઓપ્શન સાચો છે કે નહીં તે ચેક કરવાની સ્માર્ટ રીત
            is_correct = opt_str == correct_ans or opt_str.startswith(correct_ans) or correct_ans.startswith(opt_str)
            answers_list.append(Answer(text=opt_str, correct=is_correct))

        formatted_questions.append(
            QuestionResponse(
                question=str(question_obj["question"]),
                answers=answers_list
            )
        )

    return formatted_questions


@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(UPLOAD_FOLDER, "book.pdf")

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        print("File 'book.pdf' saved successfully.")
        return {"message": "File uploaded successfully"}

    except Exception as e:
        print(f"Upload Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-questions/", response_model=List[QuestionResponse])
async def generate_questions(
    topic: str = Form(...),
    num_questions: int = Form(5)
):
    try:
        pdf_path = os.path.join(UPLOAD_FOLDER, "book.pdf")

        if not os.path.exists(pdf_path):
            raise HTTPException(
                status_code=400,
                detail="PDF ફાઇલ સર્વર પર મળી નથી. કૃપા કરીને પહેલા ફાઇલ ફરીથી અપલોડ કરો."
            )

        print(f"Loading docs for topic: {topic}, requested count: {num_questions}")
        ques_llm.load_docs(pdf_path)

        questions = ques_llm.get_questions(topic, num_questions)
        print(f"Received raw questions from AI: {len(questions)}")

        formatted_questions = format_questions(questions)
        return formatted_questions

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Generation Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"સર્વર ઇન્ટરનલ એરર: {str(e)}")
