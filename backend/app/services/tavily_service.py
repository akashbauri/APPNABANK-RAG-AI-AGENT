import requests
from app.core.config import settings

class TavilySearchService:
    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY
        self.url = "https://api.tavily.com/search"

    def search(self, query: str) -> str:
        payload = {
            "api_key": self.api_key,
            "query": f"Indian personal finance banking basics: {query}",
            "search_depth": "basic",
            "include_answer": True,
            "max_results": 2
        }
        try:
            response = requests.post(self.url, json=payload, timeout=8)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                context_str = "\n".join([r.get("content", "") for r in results])
                return context_str if context_str else "No search results returned."
        except Exception:
            pass
        return "Search execution failed."

tavily_service = TavilySearchService()
