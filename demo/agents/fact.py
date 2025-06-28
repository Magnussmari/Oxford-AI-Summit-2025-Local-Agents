"""
Fact Validator Agent - Validates claims and checks accuracy
"""

from .base import PresentationAgent


class FactValidator(PresentationAgent):
    """Fact Validator - uses phi4-mini for quick validation."""
    
    def __init__(self):
        super().__init__(
            name="Fact Validator",
            model="phi4-mini",
            role="validator",
            temperature=0.1
        )
        self.timeout = 240  # 4 minute for validation
        
    async def validate(self, content: str, stream_callback=None) -> str:
        """Validate key claims in content."""
        prompt = f"""Fact-check this content:

{content[:1000]}  # Limited for speed

Identify and validate 3-5 key claims. For each:
1. State the claim
2. Assess validity (High/Medium/Low confidence)
3. Note any concerns

Be concise - this is for a live demo."""

        return await self.run(prompt, stream_callback)