import json
import os

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from template import SYSTEM_MSG, USER_MSG


class QuizCrafter:
    def __init__(self) -> None:
        self.system = SYSTEM_MSG
        self.user = USER_MSG

        # Embeddings (Free Local)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # Groq LLM
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.3-70b-versatile",
            temperature=0.7,
        )

    def load_docs(self, file_path):
        print("Loading document...")
        self._load_docs(file_path)
        print("Document loaded successfully.")
        return self.documents

    def _load_docs(self, file_path):
        loader = PyMuPDFLoader(file_path)
        self.documents = loader.load()

    def split_docs(self, documents, chunk_size=700, chunk_overlap=20):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        docs = text_splitter.split_documents(documents)
        return docs

    def get_similar_docs(self, index, query, k=4):
        return index.similarity_search(query=query, k=k)

    def create_index(self):
        print("Creating FAISS Index...")

        docs = self.split_docs(self.documents)

        self.index = FAISS.from_documents(
            documents=docs,
            embedding=self.embeddings
        )

        print("Index created successfully.")
        return self.index

    def load_chat_msg(self, topic):
        print("Loading Chat Template...")

        index = self.create_index()

        query_docs = self.get_similar_docs(
            index=index,
            query=topic,
            k=4
        )

        text = "\n".join(
            [doc.page_content for doc in query_docs]
        )

        messages = [
            SystemMessage(content=self.system),
            HumanMessage(
                content=self.user.format(context=text)
            ),
        ]

        print("Chat Template Loaded.")
        return messages

    def get_questions(self, topic):
        print("Requesting questions...")

        msg = self.load_chat_msg(topic)

        result = self.llm.invoke(msg)

        result = str(result.content).strip()

        if result.startswith("```json"):
            result = result[7:]

        if result.endswith("```"):
            result = result[:-3]

        result = result.strip()

        try:
            questions = json.loads(result)

            with open("questions.json", "w", encoding="utf-8") as f:
                json.dump(
                    questions,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

            print("Questions Generated Successfully.")
            return questions

        except Exception as e:
            print("JSON Parse Error:", e)
            print(result)
            return []