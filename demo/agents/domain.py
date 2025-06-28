"""
Domain Specialist Agent - Provides expert domain analysis
"""

from .base import PresentationAgent, CURRENT_DATE


class DomainSpecialist(PresentationAgent):
    """Domain Specialist - uses qwen3:8b for domain expertise."""
    
    def __init__(self):
        super().__init__(
            name="Domain Specialist",
            model="qwen3:8b",
            role="expert",
            temperature=0.2
        )
        self.timeout = 240  # 4 minutes for analysis
        
    async def analyze(self, query: str, domain: str, stream_callback=None) -> str:
        """Provide domain-specific analysis."""
        prompt = f"""As a {domain} domain specialist, analyze this query:

Query: {query}
Today's date: {CURRENT_DATE}

Provide expert analysis covering:
1. Core concepts and principles
2. Current state of the field
3. Key challenges and opportunities
4. Future implications

Keep response concise (2-3 paragraphs) for live demo."""

        return await self.run(prompt, stream_callback)