from textblob import TextBlob
from bs4 import BeautifulSoup
import requests


def _fetch_text_from_url(url: str, timeout: int = 8) -> str:
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "CrewAI-Bot/1.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        article = soup.find("article") or soup.find("main") or soup
        texts = " ".join(t.get_text(" ", strip=True) for t in article.find_all(["p", "h1", "h2", "h3"]))
        return texts.strip()
    except Exception:
        return ""


def analyze_sentiment_for_urls(urls: list) -> list:
    """Fetch each URL, extract text, and compute sentiment using TextBlob.

    Returns list of dicts: {url, excerpt, polarity, subjectivity, label}
    """
    results = []
    for url in urls:
        text = _fetch_text_from_url(url)
        excerpt = text[:800] if text else ""
        if not text:
            results.append({"url": url, "excerpt": excerpt, "polarity": None, "subjectivity": None, "label": "failed"})
            continue
        tb = TextBlob(text)
        polarity = round(tb.sentiment.polarity, 3)
        subjectivity = round(tb.sentiment.subjectivity, 3)
        if polarity > 0.15:
            label = "positive"
        elif polarity < -0.15:
            label = "negative"
        else:
            label = "neutral"
        results.append({
            "url": url,
            "excerpt": excerpt,
            "polarity": polarity,
            "subjectivity": subjectivity,
            "label": label,
        })
    return results
