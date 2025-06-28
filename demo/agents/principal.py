"""
Principal Synthesizer Agent - Orchestrates multi-agent research
"""

import json
import re
from typing import Dict, Any, List
from loguru import logger
from .base import PresentationAgent, CURRENT_DATE


class PrincipalSynthesizer(PresentationAgent):
    """Principal Synthesizer - uses deepseek-r1:8b for orchestration."""
    
    def __init__(self):
        super().__init__(
            name="Principal Synthesizer",
            model="deepseek-r1:8b",
            role="orchestrator",
            temperature=0.1
        )
        self.timeout = 360  # 6 minutes for deep reasoning
    
    async def analyze_query(self, query: str, stream_callback=None) -> Dict[str, Any]:
        """Analyze query and determine agent selection."""
        prompt = f"""<Thinking>
Today is {CURRENT_DATE}. I need to analyze this query to determine:
1. Complexity level (simple/moderate/complex)
2. Domain classification
3. Required specialist agents
4. Optimal processing strategy
</Thinking>

Analyze this query for multi-agent processing:
Query: {query}

Provide analysis in JSON format:
{{
    "complexity": "simple|moderate|complex",
    "domain": "technology|science|business|health|general",
    "agents_needed": ["Domain Specialist", "Web Harvester"],
    "strategy": "parallel|sequential",
    "key_aspects": ["aspect1", "aspect2"]
}}"""

        response = await self.run(prompt, stream_callback)
        
        try:
            json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
            
        return {
            "complexity": "moderate",
            "domain": "general",
            "agents_needed": ["Domain Specialist", "Web Harvester"],
            "strategy": "parallel",
            "key_aspects": ["main topic", "current state"]
        }
    
    async def synthesize_findings(self, query: str, findings: Dict[str, str], stream_callback=None, websites: List[Dict[str, str]] = None) -> str:
        """Synthesize agent findings into coherent report."""
        findings_text = "\n\n".join(
            f"=== {agent} ===\n{content[:500]}"  # Limit for speed
            for agent, content in findings.items()
        )
        
        prompt = f"""Synthesize these multi-agent findings into a coherent report:

Query: {query}

Agent Findings:
{findings_text}

IMPORTANT: Provide ONLY the final report content. Do not include any thinking, reasoning, or meta-commentary.
Start directly with the report content.

Create a concise synthesis that:
1. Combines insights from all agents
2. Resolves any conflicts
3. Highlights key findings
4. Provides actionable conclusions

Format the output as a clean markdown report with:
- A brief executive summary
- Key findings section
- Conclusion

Keep it brief for presentation (3-4 paragraphs total)."""

        # Add references if available
        if websites and len(websites) > 0:
            prompt += "\n\nAlso include a 'References' section at the end with these sources:\n"
            for site in websites:
                title = site.get('title', 'Unknown')
                url = site.get('url', '#')
                prompt += f"- [{title}]({url})\n"

        response = await self.run(prompt, stream_callback)
        
        # Clean up the response - remove thinking/reasoning if present
        lines = response.split('\n')
        cleaned_lines = []
        skip_until_content = False
        
        for line in lines:
            # Skip lines that look like thinking or meta-commentary
            if any(phrase in line.lower() for phrase in ['okay,', 'i need to', 'looking at', 'the user', 'let me']):
                skip_until_content = True
                continue
            
            # Start collecting when we hit actual content
            if skip_until_content and (line.startswith('#') or line.startswith('**') or line.strip() == ''):
                skip_until_content = False
            
            if not skip_until_content:
                cleaned_lines.append(line)
        
        # Join and clean up extra whitespace
        cleaned_response = '\n'.join(cleaned_lines).strip()
        
        # If we still have thinking content, try to extract just the report
        if 'executive summary' in cleaned_response.lower() or '# ' in cleaned_response:
            # Find the start of the actual report
            report_match = re.search(r'(#.*?Executive Summary.*)', cleaned_response, re.DOTALL | re.IGNORECASE)
            if report_match:
                cleaned_response = report_match.group(1)
        
        return cleaned_response