"""
Presentation Orchestrator - Manages multi-agent collaboration
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, Any, List
from loguru import logger

from .principal import PrincipalSynthesizer
from .domain import DomainSpecialist
from .web import WebHarvester
from .fact import FactValidator
from .quality import QualityAuditor


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
                "type": "agent_start",
                "agent": "Principal Synthesizer",
                "message": "Analyzing query"
            })
        
        analysis = await self.principal.analyze_query(query, stream_callback)
        
        if stream_callback:
            await stream_callback({
                "type": "agent_complete",
                "agent": "Principal Synthesizer"
            })
        
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
                    "type": "agent_start",
                    "agent": "Fact Validator",
                    "message": "Validating findings"
                })
            
            combined = " ".join(findings.values())[:1000]
            validation = await self.fact_validator.validate(combined, stream_callback)
            findings["Fact Validator"] = validation
            
            if stream_callback:
                await stream_callback({
                    "type": "agent_complete",
                    "agent": "Fact Validator"
                })
        
        # Phase 4: Synthesis
        if stream_callback:
            await stream_callback({
                "type": "agent_start",
                "agent": "Principal Synthesizer",
                "message": "Synthesizing findings"
            })
        
        final_report = await self.principal.synthesize_findings(query, findings, stream_callback)
        
        if stream_callback:
            await stream_callback({
                "type": "agent_complete",
                "agent": "Principal Synthesizer"
            })
        
        # Phase 5: Quality Audit (optional)
        quality_score = None
        if mode == "expert":
            if stream_callback:
                await stream_callback({
                    "type": "agent_start",
                    "agent": "Quality Auditor",
                    "message": "Auditing quality"
                })
            
            quality_score = await self.quality_auditor.audit(final_report, stream_callback)
            
            if stream_callback:
                await stream_callback({
                    "type": "agent_complete",
                    "agent": "Quality Auditor"
                })
        
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
        if callback:
            await callback({
                "type": "agent_start",
                "agent": "Domain Specialist",
                "message": f"Analyzing {analysis.get('domain', 'general')} domain"
            })
        domain = analysis.get("domain", "general")
        result = await self.domain_specialist.analyze(query, domain, callback)
        if callback:
            await callback({
                "type": "agent_complete",
                "agent": "Domain Specialist"
            })
        return ("Domain Specialist", result)
    
    async def _run_web_harvester(self, query: str, analysis: Dict[str, Any], callback):
        """Run web harvester."""
        if callback:
            await callback({
                "type": "agent_start",
                "agent": "Web Harvester",
                "message": "Searching web for latest information"
            })
        aspects = analysis.get("key_aspects", ["current information", "recent updates"])
        result = await self.web_harvester.search(query, aspects, callback)
        if callback:
            await callback({
                "type": "agent_complete",
                "agent": "Web Harvester"
            })
        return ("Web Harvester", result)