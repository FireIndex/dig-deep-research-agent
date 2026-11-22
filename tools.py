from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from functools import lru_cache
from datetime import datetime
from dotenv import load_dotenv
import logging
from log_config import setup_logging

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)

if not os.getenv("TAVILY_API_KEY"):
    logger.warning("TAVILY_API_KEY is not set")

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


# cached: an identical query / URL never hits the network twice
@lru_cache(maxsize=128)
def _search(query: str) -> str:
    logger.info("Tavily search (cache miss): %r", query)
    results = tavily.search(query=query, max_results=3)
    out = [
        f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
        for r in results['results']
    ]
    return "\n----\n".join(out)


@lru_cache(maxsize=128)
def _scrape(url: str) -> str:
    logger.info("Scraping (cache miss): %s", url)
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)[:3000]
        logger.info("Scraped %s (status %s, %d chars)", url, resp.status_code, len(text))
        return text
    except Exception as e:
        logger.exception("Scrape failed: %s", url)
        return f"Could not scrape URL: {str(e)}"


@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic . Returns Titles , URLs and snippets."""
    logger.info("web_search tool called")
    return _search(query.strip().lower())


@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    logger.info("scrape_url tool called")
    return _scrape(url)


@tool
def date_today() -> str:
    """Returns current local date and time (YYYY-MM-DD HH:MM:SS)"""
    logger.info("date_today tool called")
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
