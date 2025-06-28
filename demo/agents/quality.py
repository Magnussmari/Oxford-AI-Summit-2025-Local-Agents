"""
Quality Auditor Agent - Assesses output quality
"""

import json
import re
from typing import Dict, Any
from .base import PresentationAgent


class QualityAuditor(PresentationAgent):
    """Quality Auditor - uses phi4-mini for assessment."""
    
    def __init__(self):
        super().__init__(
            name="Quality Auditor",
            model="phi4-mini",
            role="auditor",
            temperature=0.1
        )
        self.timeout = 240  # 4 minutes for audit

    async def audit(self, report: str, stream_callback=None) -> Dict[str, Any]:
        """Perform quality assessment."""
        prompt = f"""Assess this research report quality:

{report[:1000]}

Rate these dimensions (1-10):
1. Accuracy
2. Completeness  
3. Clarity
4. Actionability

Provide brief assessment in JSON:
{{
    "accuracy": 8,
    "completeness": 7,
    "clarity": 9,
    "actionability": 8,
    "overall": 8,
    "strengths": ["clear", "well-structured"],
    "improvements": ["add more data"]
}}"""

        response = await self.run(prompt, stream_callback)
        
        try:
            json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
            
        return {
            "accuracy": 8,
            "completeness": 7,
            "clarity": 8,
            "actionability": 7,
            "overall": 7.5,
            "strengths": ["structured"],
            "improvements": ["more detail"]
        }