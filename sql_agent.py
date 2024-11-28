from langchain_community.utilities.sql_database import SQLDatabase
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import create_sql_agent
from langchain.agents import AgentType
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLDatabase.from_uri("sqlite:///chw_app.db")

api_key=os.getenv('GROQ_API_KEY')

'''
llm = ChatGroq(
    model="llama-3.2-3b-preview",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=api_key
    # other params...
)
'''

llm = ChatOpenAI(temperature=0)

agent_executor = create_sql_agent(
    llm, db = db, agent_type = "openai-tools", verbose = True
)

def execute_query(query):
    response = agent_executor.invoke({"input": query})
    return response["output"]