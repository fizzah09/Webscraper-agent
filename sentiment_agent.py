from crewai import Agent
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os

load_dotenv()

def get_sentiment_agent():
    """Create and return the Sentiment Agent"""
def _create_llm(model: str = None, temperature: float = 0.3) -> ChatOpenAI:
    load_dotenv()
    model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        return ChatOpenAI(model=model, temperature=temperature, api_key=openai_key)

    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_key:
        raise ValueError("Missing API key: set OPENAI_API_KEY or OPENROUTER_API_KEY in .env")

    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    extra_headers = {
        "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "http://localhost"),
        "X-Title": os.getenv("OPENROUTER_APP_NAME", "CrewAI App"),
    }
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=openrouter_key,
        base_url=base_url,
        model_kwargs={"extra_headers": extra_headers},
    )


def get_sentiment_agent():
    """Create and return the Sentiment Agent"""
    llm = _create_llm(model=os.getenv("LLM_MODEL", "gpt-4o-mini"), temperature=0.3)
    
    return Agent(
        name="Sentiment Agent",
        role="Evaluates sentiment polarity for each blog",
        goal="Produce a sentiment summary and aggregate engagement indicators",
        backstory="Expert at understanding emotional tone and public sentiment in written content",
        llm=llm, 
        verbose=True,
        allow_delegation=False
    )

# Backward-compatible export used by older code
# Defer creation to runtime to avoid initializing crewai executors at import time.
SentimentAgent = None
