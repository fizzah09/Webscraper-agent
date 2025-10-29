from crewai import Agent
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
import requests
from bs4 import BeautifulSoup

load_dotenv()

def _create_llm(model: str = None, temperature: float = 0.2) -> ChatOpenAI:
    """Create a ChatOpenAI LLM using OpenAI if OPENAI_API_KEY is set, else OpenRouter."""
    load_dotenv()
    model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        return ChatOpenAI(model=model, temperature=temperature, api_key=openai_key)

    # Fallback to OpenRouter
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


def get_crawler_agent():
    llm = _create_llm(model=os.getenv("LLM_MODEL", "gpt-4o-mini"), temperature=0.2)
    
    return Agent(
        name="Crawler Agent",
        role="Web crawler that scrapes blogs for a given keyword",
        goal="Collect and return text content of top 10 blog posts",
        backstory="An ethical crawler that respects robots.txt and rate limits.",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

# Backward-compatible export used by older code
# Defer creation to runtime to avoid initializing crewai executors at import time.
CrawlerAgent = None


def search_duckduckgo(query: str, max_results: int = 10, timeout: int = 10) -> list:
    """Perform a lightweight DuckDuckGo HTML search and return a list of result URLs.

    This is a simple, no-key-required search that scrapes DuckDuckGo's HTML results page.
    It is suitable for small experiments and demo purposes. For production/large scale use,
    use a search API (SerpAPI, Bing, Google) and respect terms of service.
    """
    try:
        # Prefer GET with query params for broader compatibility
        resp = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers={"User-Agent": "CrewAI-Bot/1.0"},
            timeout=timeout,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        links = []
        # First try known DuckDuckGo result anchors
        for a in soup.select("a.result__a"):
            href = a.get("href")
            if href and href.startswith("http"):
                links.append(href)
            if len(links) >= max_results:
                break

        # Fallback: collect any absolute http(s) hrefs on the page (broader but noisier)
        if len(links) < max_results:
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if href.startswith("http") and href not in links:
                    links.append(href)
                if len(links) >= max_results:
                    break
        # dedupe while preserving order
        seen = set()
        out = []
        for u in links:
            if u in seen:
                continue
            seen.add(u)
            out.append(u)
        return out
    except Exception:
        # If DuckDuckGo scraping fails for any reason, return empty and allow caller to try alternatives
        pass

    # Fallback: try Bing HTML search (may return redirecting URLs which requests will follow)
    try:
        bresp = requests.get("https://www.bing.com/search", params={"q": query}, headers={"User-Agent": "Mozilla/5.0"}, timeout=timeout)
        bresp.raise_for_status()
        bsoup = BeautifulSoup(bresp.text, "html.parser")
        links = []
        for li in bsoup.select('li.b_algo'):
            a = li.find('a', href=True)
            if a:
                href = a['href']
                if href.startswith('http'):
                    links.append(href)
            if len(links) >= max_results:
                break
        # dedupe
        seen = set(); out = []
        for u in links:
            if u in seen: continue
            seen.add(u); out.append(u)
        return out
    except Exception:
        return []
    

def search_bing(query: str, max_results: int = 10, timeout: int = 10) -> list:
    """Search Bing and return a list of result hrefs (may be redirecting Bing URLs)."""
    try:
        bresp = requests.get("https://www.bing.com/search", params={"q": query}, headers={"User-Agent": "Mozilla/5.0"}, timeout=timeout)
        bresp.raise_for_status()
        bsoup = BeautifulSoup(bresp.text, "html.parser")
        links = []
        for li in bsoup.select('li.b_algo'):
            a = li.find('a', href=True)
            if a:
                href = a['href']
                if href.startswith('http'):
                    links.append(href)
            if len(links) >= max_results:
                break
        # dedupe
        seen = set(); out = []
        for u in links:
            if u in seen: continue
            seen.add(u); out.append(u)
        return out
    except Exception:
        return []


def resolve_final_urls(urls: list, timeout: int = 8) -> list:
    """Follow redirects for each URL (HEAD first, then GET) and return final targets.

    This helps clean up redirecting search result URLs (e.g., Bing ck/ links) to the real targets.
    """
    out = []
    for u in urls:
        try:
            # Try HEAD to follow redirects quickly
            r = requests.head(u, allow_redirects=True, timeout=timeout)
            final = r.url if r.ok else u
            # If HEAD returned the same or not ok, try GET as a fallback
            if final == u or not r.ok:
                r2 = requests.get(u, allow_redirects=True, timeout=timeout)
                final = r2.url if r2.ok else u
            out.append(final)
        except Exception:
            out.append(u)
    # dedupe preserving order
    seen = set(); res = []
    for v in out:
        if v in seen: continue
        seen.add(v); res.append(v)
    return res
