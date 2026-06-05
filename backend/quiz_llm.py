import json
import os

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from template import SYSTEM_MSG, USER_MSG

class QuizCrafter:
def init(self) -> None:
self.system = SYSTEM_MSG
self.user = USER_MSG

    self.llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0.7,
    )

    self.documents = []

def load_docs(self, file_path):
    print("Loading document...")

    loader = PyMuPDFLoader(file_path)
    self.documents = loader.load()

    print("Document loaded successfully.")
    return self.documents

def load_chat_msg(self, topic):
    print("Preparing context...")

    text = ""

    # Render free plan ke liye limited pages
    for doc in self.documents[:20]:
        text += doc.page_content + "\n"

    context = text[:12000]

    messages = [
        SystemMessage(content=self.system),
        HumanMessage(
            content=self.user.format(
                context=context,
                topic=topic
            )
        ),
    ]

    return messages

def get_questions(self, topic):
    print("Generating questions...")

    messages = self.load_chat_msg(topic)

    result = self.llm.invoke(messages)
    result = str(result.content).strip()

    if result.startswith("```json"):
        result = result[7:]

    if result.endswith("```"):
        result = result[:-3]

    result = result.strip()

    try:
        questions = json.loads(result)

        with open(
            "questions.json",
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                questions,
                f,
                indent=4,
                ensure_ascii=False
            )

        print("Questions generated successfully.")
        return questions

    except Exception as e:
        print("JSON Parse Error:", e)
        print(result)
        return []