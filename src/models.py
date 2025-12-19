import os
import sqlite3
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain.tools import tool
from datetime import datetime
from langchain_community.utilities import SQLDatabase
from langgraph.runtime import get_runtime
from dataclasses import dataclass

load_dotenv()


# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
db = SQLDatabase.from_uri("sqlite:///appointments.db")

# System prompt
PROMPT = """You are an experienced English teacher.
Your job is:
- Teach English like a real tutor
- Correct grammar mistakes
- Explain in simple language
- Ask practice questions
- Adapt to student's level
- Encourage improvement
- Track mistakes and improve weak areas
- Ask short answer questions to practice speaking
- Ask user for taking a short test for determining their level
- Remember the info about the student and use it in future lessons from the conversation
- Ask user's name and use it in the conversation
- Remember the user’s name and level
- Keep track of common mistakes and focus on them
- Build on previous topics and exercises
-Use tools to answer about time and date
-If user asks about appointments, use the database tool to query the appointments database
-If user wants to schedule an appointment, guide them through the process and use the database tool to add the appointment
-If the time that user wants is not available, suggest alternative times

Rules:
- Always respond in English
- When user makes a mistake, correct it politely
- Give short exercises
- If user asks to learn a topic, teach step-by-step
- Never answer like a chatbot, answer like a teacher
"""

# Setup SQLite connection and checkpointer
conn = sqlite3.connect("memory.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)


# Setup models
@dataclass
class RuntimeContext:
    db: SQLDatabase

@tool
def get_current_time() -> str:
    """
    Return current local time as a string.
    Example: '2025-12-11 10:45'
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")
@tool
def execute_sql(query: str) -> str:
    """Execute a SQLite command and return results."""
    runtime = get_runtime(RuntimeContext)
    db = runtime.context.db

    try:
        return db.run(query)
    except Exception as e:
        return f"Error: {e}"


model_openai = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    openai_api_base=OPENAI_API_BASE,
    temperature=0,
    
)

model_ollama = ChatOllama(
    model=OLLAMA_MODEL,
    host=OLLAMA_HOST,
    temperature=0,
)

# Create agents with persistent memory
agent_openai = create_agent(
    model=model_openai,
    tools=[get_current_time,execute_sql],
    system_prompt=PROMPT,
    checkpointer=checkpointer,
    context_schema=RuntimeContext
)

agent_ollama = create_agent(
    model=model_ollama,
    tools=[get_current_time, execute_sql],
    system_prompt=PROMPT,
    checkpointer=checkpointer,
    context_schema=RuntimeContext
)


# Thread configuration
THREAD_ID = "session5"
CFG = {"configurable": {"thread_id": THREAD_ID}}


# Functions to generate responses
def generate_openai(prompt: str, model_name: str = "gpt-4o"):
    """Generate response using OpenAI model. Return error if something goes wrong."""
    try:
        model_openai.model_name = model_name
        res = agent_openai.invoke(
            {"messages": [{"role": "user", "content": prompt}]},
            config=CFG,
            context=RuntimeContext(db=db)
        )
        return res["messages"][-1].content
    except Exception as e:
        return f"[ERROR] {e}"

def generate_ollama(prompt: str, model_name: str = None):
    """Generate response using Ollama model. Return error if something goes wrong."""
    try:
        model_ollama.model = OLLAMA_MODEL
        res = agent_ollama.invoke(
            {"messages": [{"role": "user", "content": prompt}]},
            config=CFG,
            context=RuntimeContext(db=db)
        )
        return res["messages"][-1].content
    except Exception as e:
        return f"[ERROR] {e}"

    