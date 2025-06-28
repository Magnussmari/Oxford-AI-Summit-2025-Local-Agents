"""
Web Harvester Agent - Performs web research with optional Brave search
"""

import os
from typing import List, Dict, Any
from loguru import logger
import httpx
from .base import PresentationAgent, CURRENT_DATE


class WebHarvester(PresentationAgent):
    """Web Harvester - uses qwen3:4b for speed with optional Brave search."""
    
    def __init__(self):
        super().__init__(
            name="Web Harvester",
            model="qwen3:4b",
            role="researcher",
            temperature=0.3
        )
        self.timeout = 90  # 1.5 minutes for web research
        self.brave_api_key = os.getenv("BRAVE_API_KEY")
        self.has_brave = bool(self.brave_api_key)
        
    async def search(self, query: str, aspects: List[str], stream_callback=None) -> str:
        """Perform web research with real search if available."""
        web_results = ""
        websites_explored = []
        
        if self.has_brave and stream_callback:
            await stream_callback({
                "type": "web_search",
                "agent": self.name,
                "status": "searching"
            })
        
        if self.has_brave:
            try:
                search_results = await self._brave_search(query)
                if search_results:
                    web_results = "\n=== Live Web Results ===\n"
                    websites_explored = []  # Track URLs
                    
                    for i, result in enumerate(search_results[:5], 1):
                        web_results += f"{i}. {result['title']}\n   URL: {result['url']}\n   {result['description']}\n\n"
                        websites_explored.append({
                            "title": result['title'],
                            "url": result['url']
                        })
                    
                    if stream_callback:
                        await stream_callback({
                            "type": "web_results",
                            "agent": self.name,
                            "count": len(search_results),
                            "websites": websites_explored
                        })
            except Exception as e:
                logger.warning(f"Brave search failed: {e}")
        
        aspects_str = ", ".join(aspects)
        
        # Enhanced prompt to include website references
        prompt = f"""Research this query focusing on: {aspects_str}

Query: {query}
{web_results}

Provide current information (as of {CURRENT_DATE}) with the following structure:

1. **Key Findings**: 2-3 paragraphs summarizing the most important information
2. **Sources Consulted**: List the websites you referenced from the search results
3. **Additional Context**: Any relevant trends or developments

Be specific and cite which websites provided which information."""

        return await self.run(prompt, stream_callback)
    
    async def _brave_search(self, query: str, count: int = 5) -> List[Dict[str, Any]]:
        """Perform Brave search."""
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.brave_api_key
        }
        params = {
            "q": query,
            "count": count,
            "freshness": "pm"  # Past month
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                return [{
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "description": item.get("description", "")
                } for item in data.get("web", {}).get("results", [])]
            return []