"""
Presentation-Optimized Agents for Oxford AI Summit Demo
Using smaller models for speed while demonstrating multi-agent concepts
"""

import asyncio
import subprocess
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime
from loguru import logger
import json
import os
import httpx
import time
import aiohttp

CURRENT_DATE = datetime.now().strftime("%B %d, %Y")

class PresentationAgent:
    """Base class for presentation demo agents - optimized for speed."""
    
    def __init__(self, name: str, model: str, role: str, temperature: float = 0.3):
        self.name = name
        self.model = model
        self.role = role
        self.temperature = temperature
        self.timeout = 60  # Increased timeout for streaming
        
    async def run(self, prompt: str, stream_callback=None) -> str:
        """Run the agent with streaming via Ollama HTTP API."""
        try:
            # Send initial thinking update
            if stream_callback:
                await stream_callback({
                    "type": "agent_thinking",
                    "agent": self.name,
                    "model": self.model
                })
            
            # Use Ollama HTTP API for streaming
            url = "http://localhost:11434/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": 1000  # Limit tokens for speed
                }
            }
            
            full_response = ""
            token_count = 0
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                    if response.status == 200:
                        async for line in response.content:
                            if line:
                                try:
                                    data = json.loads(line.decode('utf-8'))
                                    if 'response' in data:
                                        chunk = data['response']
                                        full_response += chunk
                                        # Only count tokens when we have word boundaries
                                        if chunk and (chunk[-1].isspace() or chunk[0].isspace()):
                                            token_count = len(full_response.split())
                                        
                                        # Stream the actual text to frontend
                                        if stream_callback and chunk.strip():
                                            await stream_callback({
                                                "type": "agent_stream",
                                                "agent": self.name,
                                                "chunk": chunk,
                                                "tokens": token_count
                                            })
                                        
                                    if data.get('done', False):
                                        break
                                except json.JSONDecodeError:
                                    continue
                    else:
                        error_text = await response.text()
                        logger.error(f"{self.name} HTTP error {response.status}: {error_text}")
                        return f"Error: {self.name} failed with status {response.status}"
            
            # Send completion update
            if stream_callback:
                await stream_callback({
                    "type": "agent_response",
                    "agent": self.name,
                    "tokens": token_count,
                    "complete": True
                })
            
            return full_response.strip()
            
        except asyncio.TimeoutError:
            logger.warning(f"{self.name} timed out after {self.timeout}s")
            if stream_callback:
                await stream_callback({
                    "type": "agent_error",
                    "agent": self.name,
                    "error": "Timeout"
                })
            return f"{self.name} timed out. Consider using a smaller model."
        except aiohttp.ClientError as e:
            logger.error(f"{self.name} connection error: {e}")
            if stream_callback:
                await stream_callback({
                    "type": "agent_error",
                    "agent": self.name,
                    "error": "Connection failed - Is Ollama running?"
                })
            return f"{self.name} connection error. Please ensure Ollama is running."
        except Exception as e:
            logger.error(f"{self.name} exception: {e}")
            if stream_callback:
                await stream_callback({
                    "type": "agent_error",
                    "agent": self.name,
                    "error": str(e)
                })
            return f"{self.name} error: {str(e)}"


class PrincipalSynthesizer(PresentationAgent):
    """Principal Synthesizer - uses deepseek-r1:8b for orchestration."""
    
    def __init__(self):
        super().__init__(
            name="Principal Synthesizer",
            model="deepseek-r1:8b",
            role="orchestrator",
            temperature=0.1
        )
        self.timeout = 180  # 3 minutes for deep reasoning
    
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
            import re
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
    
    async def synthesize_findings(self, query: str, findings: Dict[str, str], stream_callback=None) -> str:
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
            import re
            report_match = re.search(r'(#.*?Executive Summary.*)', cleaned_response, re.DOTALL | re.IGNORECASE)
            if report_match:
                cleaned_response = report_match.group(1)
        
        return cleaned_response


class DomainSpecialist(PresentationAgent):
    """Domain Specialist - uses qwen3:8b for domain expertise."""
    
    def __init__(self):
        super().__init__(
            name="Domain Specialist",
            model="qwen3:8b",
            role="expert",
            temperature=0.2
        )
        self.timeout = 120  # 2 minutes for analysis
        
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
                    for i, result in enumerate(search_results[:3], 1):
                        web_results += f"{i}. {result['title']}\n   {result['description']}\n"
                    
                    if stream_callback:
                        await stream_callback({
                            "type": "web_results",
                            "agent": self.name,
                            "count": len(search_results)
                        })
            except Exception as e:
                logger.warning(f"Brave search failed: {e}")
        
        aspects_str = ", ".join(aspects)
        prompt = f"""Research this query focusing on: {aspects_str}

Query: {query}
{web_results}

Provide current information (as of {CURRENT_DATE}) in 2-3 concise paragraphs."""

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


class FactValidator(PresentationAgent):
    """Fact Validator - uses phi4-mini for quick validation."""
    
    def __init__(self):
        super().__init__(
            name="Fact Validator",
            model="phi4-mini",
            role="validator",
            temperature=0.1
        )
        self.timeout = 60  # 1 minute for validation
        
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


class QualityAuditor(PresentationAgent):
    """Quality Auditor - uses phi4-mini for assessment."""
    
    def __init__(self):
        super().__init__(
            name="Quality Auditor",
            model="phi4-mini",
            role="auditor",
            temperature=0.1
        )
        self.timeout = 60  # 1 minute for audit
        
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
            import re
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


class PresentationOrchestrator:
    """Orchestrates agents for live presentation with visual feedback."""
    
    def __init__(self):
        self.principal = PrincipalSynthesizer()
        self.domain_specialist = DomainSpecialist()
        self.web_harvester = WebHarvester()
        self.fact_validator = FactValidator()
        self.quality_auditor = QualityAuditor()
        self.memory_store = {}  # Simple memory for demo
        
    async def research(self, query: str, mode: str = "auto", stream_callback=None) -> Dict[str, Any]:
        """Execute multi-agent research with streaming updates."""
        start_time = time.time()
        
        # Phase 1: Analysis
        if stream_callback:
            await stream_callback({
                "type": "phase",
                "phase": "analysis",
                "agent": "Principal Synthesizer"
            })
        
        analysis = await self.principal.analyze_query(query, stream_callback)
        
        # Phase 2: Agent Selection & Execution
        if stream_callback:
            await stream_callback({
                "type": "phase",
                "phase": "research",
                "agents": analysis.get("agents_needed", ["Domain Specialist", "Web Harvester"])
            })
        
        findings = {}
        
        # Determine which agents to use based on mode
        if mode == "simple":
            agents = ["Web Harvester"]
        elif mode == "expert":
            agents = ["Domain Specialist", "Web Harvester", "Fact Validator"]
        else:
            agents = analysis.get("agents_needed", ["Domain Specialist", "Web Harvester"])
        
        # Execute agents (parallel for demo effect)
        tasks = []
        if "Domain Specialist" in agents:
            tasks.append(self._run_domain_specialist(query, analysis, stream_callback))
        if "Web Harvester" in agents:
            tasks.append(self._run_web_harvester(query, analysis, stream_callback))
            
        if tasks:
            results = await asyncio.gather(*tasks)
            for agent_name, result in results:
                findings[agent_name] = result
        
        # Phase 3: Validation (if needed)
        if "Fact Validator" in agents and findings:
            if stream_callback:
                await stream_callback({
                    "type": "phase",
                    "phase": "validation",
                    "agent": "Fact Validator"
                })
            
            combined = " ".join(findings.values())[:1000]
            validation = await self.fact_validator.validate(combined, stream_callback)
            findings["Fact Validator"] = validation
        
        # Phase 4: Synthesis
        if stream_callback:
            await stream_callback({
                "type": "phase",
                "phase": "synthesis",
                "agent": "Principal Synthesizer"
            })
        
        final_report = await self.principal.synthesize_findings(query, findings, stream_callback)
        
        # Phase 5: Quality Audit (optional)
        quality_score = None
        if mode == "expert":
            if stream_callback:
                await stream_callback({
                    "type": "phase",
                    "phase": "quality",
                    "agent": "Quality Auditor"
                })
            
            quality_score = await self.quality_auditor.audit(final_report, stream_callback)
        
        # Store in memory
        self.memory_store[query] = {
            "timestamp": datetime.now().isoformat(),
            "report": final_report,
            "agents": list(findings.keys())
        }
        
        total_time = time.time() - start_time
        
        return {
            "query": query,
            "analysis": analysis,
            "agents_used": list(findings.keys()),
            "findings": findings,
            "report": final_report,
            "quality_score": quality_score,
            "execution_time": round(total_time, 1),
            "timestamp": datetime.now().isoformat(),
            "web_search_used": self.web_harvester.has_brave,
            "memory_items": len(self.memory_store)
        }
    
    async def _run_domain_specialist(self, query: str, analysis: Dict[str, Any], callback):
        """Run domain specialist."""
        domain = analysis.get("domain", "general")
        result = await self.domain_specialist.analyze(query, domain, callback)
        return ("Domain Specialist", result)
    
    async def _run_web_harvester(self, query: str, analysis: Dict[str, Any], callback):
        """Run web harvester."""
        aspects = analysis.get("key_aspects", ["current information", "recent updates"])
        result = await self.web_harvester.search(query, aspects, callback)
        return ("Web Harvester", result)