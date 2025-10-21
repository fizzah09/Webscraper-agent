from crewai import Agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def get_cleaner_agent():
    """Create and return the Cleaner Agent"""
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        model_kwargs={
            "extra_headers": {
                "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "http://localhost:3000"),
                "X-Title": os.getenv("OPENROUTER_APP_NAME", "CrewAI App"),
            }
        }
    )
    
    return Agent(
        name="Cleaner Agent",
        role="Text cleaner and language detector",
        goal="Clean, normalize text and detect language from crawled data",
        backstory="Expert at cleaning and normalizing text data, detecting languages, and preparing content for analysis",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

# Create agent instance
CleanerAgent = get_cleaner_agent()
