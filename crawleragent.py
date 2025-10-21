from crewai import Agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def get_crawler_agent():
    """Create and return the Crawler Agent"""
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
        name="Crawler Agent",
        role="Web crawler that scrapes blogs for a given keyword",
        goal="Collect and return text content of top 10 blog posts",
        backstory="An ethical crawler that respects robots.txt and rate limits.",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

# Create agent instance
CrawlerAgent = get_crawler_agent()
