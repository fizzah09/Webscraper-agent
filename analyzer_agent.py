from crewai import Agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def get_analyzer_agent():
    """Create and return the Analyzer Agent"""
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
        name="Analyzer Agent",
        role="Performs topic, tone, and motive analysis",
        goal="Identify what themes and emotions dominate in the content",
        backstory="Expert analyst specialized in extracting insights from text content",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

# Create agent instance
AnalyzerAgent = get_analyzer_agent()
