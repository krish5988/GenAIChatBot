import os
import google.generativeai as genai
import textwrap
from IPython.display import display
from IPython.display import Markdown
from dotenv import load_dotenv
load_dotenv()
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate

class queryDocs:
    chain=None
    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    def to_markdown(self,text):
        self.text = self.text.replace('•', '  *')
        return Markdown(textwrap.indent(self.text, '> ', predicate=lambda _: True))
    def get_pdf_txt(self,pdf_docs):
        text=""
        # for pdf in pdf_docs:
        pdf_reader=PdfReader(pdf_docs)
        print(len(pdf_reader.pages))
        for page in pdf_reader.pages:
            text=text+page.extract_text()
        return text
    @staticmethod
    def get_txt_chunks(text):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=100000, chunk_overlap=1000)
        chunks = text_splitter.split_text(text)
        return chunks
    @staticmethod
    def get_vector_store(text_chunks):
        embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
        vector_store.save_local("faiss_index")
    @staticmethod    
    def get_conversational_chain():

        prompt_template = """
        Answer the question as detailed as possible from the provided context, make sure to provide all the details in most formatted way, if the answer is not in
        provided context just say, "answer is not available in the context"\n\n
        Context:\n {context}?\n
        Question: \n{question}\n

        Answer:
        """

        model = ChatGoogleGenerativeAI(model="gemini-pro",
                                temperature=0.3)

        prompt = PromptTemplate(template = prompt_template, input_variables = ["context", "question"])
        
        queryDocs.chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    @staticmethod   
    def user_input(user_question):
        embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
        new_db = FAISS.load_local("faiss_index", embeddings,allow_dangerous_deserialization=True)
        docs = new_db.similarity_search(user_question)
        # response = chain.invoke(user_question)
        response = queryDocs.chain(
            {"input_documents":docs, "question": user_question}
            , return_only_outputs=True)

        return response
    @staticmethod
    def augmentedUserQuery(docsTxt):
        text_chunks=queryDocs.get_txt_chunks(docsTxt)
        queryDocs.get_vector_store(text_chunks)
        queryDocs.get_conversational_chain()
    @staticmethod
    def getQueryResponse(query):
        return queryDocs.user_input(query)


