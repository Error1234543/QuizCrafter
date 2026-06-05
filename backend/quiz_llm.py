import json
import os

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import FakeEmbeddings

from template import SYSTEM_MSG, USER_MSG


class QuizCrafter:
    def __init__(self):
        self.system = SYSTEM_MSG
        self.user = USER_MSG

        self.embeddings = FakeEmbeddings(size=384)

        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.3-70b-versatile",
            temperature=0.7,
        )

    def load_docs(self, file_path):
        loader = PyMuPDFLoader(file_path)
        self.documents = loader.load()
        return self.documents

    def split_docs(self, documents):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=700,
            chunk_overlap=20
        )
        return splitter.split_documents(documents)

    def create_index(self):
        docs = self.split_docs(self.documents)

        self.index = FAISS.from_documents(
            docs,
            self.embeddings
        )

        return self.index

    def get_similar_docs(self, index, query, k=4):
        return index.similarity_search(query=query, k=k)

    def load_chat_msg(self, topic):
        index = self.create_index()

        query_docs = self.get_similar_docs(
            index=index,
            query=topic,
            k=4
        )

        text = "\n".join(
            [doc.page_content for doc in query_docs]
        )

        return [
            SystemMessage(content=self.system),
            HumanMessage(
                content=self.user.format(context=text)
            ),
        ]

    def get_questions(self, topic):
        msg = self.load_chat_msg(topic)

        result = self.llm.invoke(msg)

        result = str(result.content).strip()

        if result.startswith("```json"):
            result = result[7:]

        if result.endswith("```"):
            result = result[:-3]

        try:
            return json.loads(result)
        except:
            return []