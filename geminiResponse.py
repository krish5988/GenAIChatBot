from langchain.prompts import PromptTemplate,ChatPromptTemplate,HumanMessagePromptTemplate,MessagesPlaceholder
from langchain_core.messages import SystemMessage
from langchain_experimental.agents.agent_toolkits import create_python_agent
from langchain_experimental.tools.python.tool import PythonREPLTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

class geminiResponseGenerator:
    response=""

    def __init__(self) -> None:
        # print(os.getenv("GOOGLE_API_KEY"))
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.prompt  = ChatPromptTemplate.from_messages([
            SystemMessage(content="Output data in tabular format"),
            HumanMessagePromptTemplate.from_template("""create test cases in tabular html format with column Testcase ID,test case description,Test Steps,Input Data,Expected result with maximum details in test steps from  
                                                     and navigation for the test steps should start from login page,show only most confident response

                                                     Context : {content}       
                                                     """)])
        self.llm=ChatGoogleGenerativeAI(model="gemini-pro",temperature=0.3)
        self.chain=LLMChain(llm=self.llm,
               prompt=self.prompt,
               verbose=True)
    def getResponseForQuery(self,content):
        if geminiResponseGenerator.response=="":
            geminiResponseGenerator.response = self.chain.run({'content':content})
        return geminiResponseGenerator.response