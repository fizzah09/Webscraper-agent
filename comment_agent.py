from crewai import Agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

def get_comment_agent():
    """Create and return the Comment Agent"""
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
        name="Comment Generator Agent",
        role="Personalized blog comment writer",
        goal="Generate thoughtful, engaging, and personalized comments for blog posts based on sentiment and content analysis",
        backstory="""You are an expert at crafting authentic, engaging blog comments. 
        You understand context, sentiment, and can write comments that add value to discussions.
        Your comments are natural, conversational, and show genuine engagement with the content.
        You adapt your tone based on the article's sentiment and topic.
        You write comments that are 2-3 sentences long, insightful, and ready to post.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

CommentAgent = None
