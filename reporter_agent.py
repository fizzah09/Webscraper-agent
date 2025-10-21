from crewai import Agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def get_reporter_agent():
    """Create and return the Reporter Agent"""
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
        name="Reporter Agent",
        role="Summarizes insights into visual and textual reports",
        goal="Deliver an easily digestible 1-page insight brief",
        backstory="Expert at creating compelling visual reports and data summaries",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

# Create agent instance
ReporterAgent = get_reporter_agent()
