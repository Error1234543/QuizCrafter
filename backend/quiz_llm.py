import json
import os

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from template import SYSTEM_MSG, USER_MSG


class QuizCrafter:
    def __init__(self):
        self.system = SYSTEM_MSG
        self.user = USER_MSG

        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.3-70b-versatile",
            temperature=0.3,
        )

    def load_docs(self, file_path):
        loader = PyMuPDFLoader(file_path)
        self.documents = loader.load()
        return self.documents

    def load_chat_msg(self, topic, num_questions):
        full_text = "\n".join([doc.page_content for doc in self.documents])

        sys_content = (
            f"You are an expert exam paper generator. Extract or generate exactly {num_questions} multiple-choice questions "
            "from the provided document. Strictly adhere to the requested language (e.g., if the text is in Gujarati, "
            "generate questions and answers in Gujarati script)."
        )
        
        user_content = (
            f"Here is the context from the PDF:\n\n{full_text[:15000]}\n\n"  # टोकન લિમિટ સાચવવા થોડો ટેક્સ્ટ લિમિટ કર્યો
            f"Task: Based on the topic '{topic}', generate exactly {num_questions} multiple choice questions. "
            "Output must be a valid JSON array of objects. Each object must have 'question', 'options' (array of strings), and 'correct_answer' (string matching the exact starting text of the correct option)."
        )

        return [
            SystemMessage(content=sys_content),
            HumanMessage(content=user_content),
        ]

    def get_questions(self, topic, num_questions=5):
        # यहाँ हमने num_questions पास कर दिया है
        msg = self.load_chat_msg(topic, num_questions)

        result = self.llm.invoke(msg)
        result = str(result.content).strip()

        if result.startswith('```json'):
            result = result[7:]

        if result.endswith('
```'):
            result = result[:-3]

        result = result.strip()

        try:
            return json.loads(result)
        except:
            return []
