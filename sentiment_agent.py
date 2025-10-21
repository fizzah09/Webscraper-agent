from crewai import Agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def get_sentiment_agent():
    """Create and return the Sentiment Agent"""
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        temperature=0.3,
        model_kwargs={
            "extra_headers": {
                "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "http://localhost:3000"),
                "X-Title": os.getenv("OPENROUTER_APP_NAME", "CrewAI App"),
            }
        }
    )
    
    return Agent(
        name="Sentiment Agent",
        role="Evaluates sentiment polarity for each blog",
        goal="Produce a sentiment summary and aggregate engagement indicators",
        backstory="Expert at understanding emotional tone and public sentiment in written content",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

# Create agent instance
SentimentAgent = get_sentiment_agent()
