"""
Enhanced Production-Ready Orchestrator with all improvements
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

# Import enhanced components
from .principal_enhanced import ImprovedPrincipalSynthesizer
from .principal import PrincipalSynthesizer
from .domain import DomainSpecialist
from .web import WebHarvester
from .fact import FactValidator
from .quality import QualityAuditor

# Core enhancements
from .core.resilience import ResilientAgentWrapper, AgentHealthMonitor
from .core.communication import AgentCommunicationProtocol, AgentHandoff, AgentCoordinator
from .core.memory import AgentMemorySystem, MemoryEntry
from .core.dynamic import PromptCache, DynamicPromptBuilder


class ProductionOrchestrator:
    """Production-ready orchestrator with all enhancements"""
    
    def __init__(self, use_enhanced: bool = True):
        """Initialize with option to use enhanced or standard agents"""
        
        # Choose agent implementations
        if use_enhanced:
            logger.info("Initializing enhanced production orchestrator")
            self.principal = ResilientAgentWrapper(ImprovedPrincipalSynthesizer())
        else:
            logger.info("Initializing standard orchestrator")
            self.principal = PrincipalSynthesizer()
            
        # Initialize other agents with resilience wrappers
        self.domain_specialist = ResilientAgentWrapper(DomainSpecialist())
        self.web_harvester = ResilientAgentWrapper(WebHarvester())
        self.fact_validator = ResilientAgentWrapper(FactValidator())
        self.quality_auditor = ResilientAgentWrapper(QualityAuditor())
        
        # Initialize enhancement systems
        self.memory_system = AgentMemorySystem()
        self.communication = AgentCommunicationProtocol()
        self.coordinator = AgentCoordinator(self.communication)
        self.health_monitor = AgentHealthMonitor()
        self.prompt_cache = PromptCache()
        self.prompt_builder = DynamicPromptBuilder()
        
        # Set agent dependencies
        self._setup_dependencies()
        
    def _setup_dependencies(self):
        """Setup agent dependencies for coordination"""
        self.coordinator.set_dependencies("Fact Validator", ["Domain Specialist", "Web Harvester"])
        self.coordinator.set_dependencies("Quality Auditor", ["Principal Synthesizer"])
        
    async def research(self, query: str, mode: str = "auto", 
                      stream_callback=None, use_memory: bool = True) -> Dict[str, Any]:
        """Execute enhanced multi-agent research"""
        
        start_time = time.time()
        logger.info(f"Starting enhanced research for: {query}")
        
        # Check memory for similar past queries
        if use_memory:
            similar_memories = self.memory_system.retrieve_similar(query, limit=3)
            quality_score = similar_memories[0].metadata.get("quality_score", 0) if similar_memories else 0
            # Ensure quality_score is numeric (handle dict case)
            if isinstance(quality_score, dict):
                quality_score = 0
            if similar_memories and quality_score and quality_score > 0.9:
                logger.info(f"🎯 CACHE HIT: Using high-quality cached response for query: '{query[:50]}...'")
                logger.info(f"   Original query timestamp: {similar_memories[0].timestamp}")
                logger.info(f"   Quality score: {similar_memories[0].metadata.get('quality_score')}")
                if stream_callback:
                    await stream_callback({
                        "type": "cache_hit",
                        "message": "Using optimized response from memory"
                    })
                return self._format_memory_response(similar_memories[0])
                
        # Set global context
        self.communication.set_global_context("query", query)
        self.communication.set_global_context("mode", mode)
        self.communication.set_global_context("start_time", start_time)
        
        # Phase 1: Enhanced Analysis
        if stream_callback:
            await stream_callback({
                "type": "agent_start",
                "agent": "Principal Synthesizer",
                "message": "Analyzing query with enhanced reasoning"
            })
            
        # Use cached prompts if available
        analysis_prompt = self.prompt_cache.get("principal_analysis", query)
        if not analysis_prompt:
            # Principal will build its own structured prompt
            # Access the wrapped agent's method if using resilient wrapper
            if hasattr(self.principal, 'agent'):
                analysis = await self.principal.agent.analyze_query(query, stream_callback)
            else:
                analysis = await self.principal.analyze_query(query, stream_callback)
        else:
            if hasattr(self.principal, 'agent'):
                analysis = await self.principal.agent.run(analysis_prompt, stream_callback)
            else:
                analysis = await self.principal.run(analysis_prompt, stream_callback)
            
        # Record analysis success
        if isinstance(analysis, dict) and "complexity" in analysis:
            self.prompt_cache.store(
                "principal_analysis", 
                query, 
                "structured_analysis_prompt",  # Placeholder
                success=True,
                response_quality=0.9
            )
            
        if stream_callback:
            await stream_callback({
                "type": "agent_complete",
                "agent": "Principal Synthesizer"
            })
            
        # Create handoff for next agents
        analysis_handoff = AgentHandoff(
            from_agent="Principal Synthesizer",
            to_agent="Multiple",
            query=query,
            key_findings={
                "complexity": analysis.get("complexity", "moderate"),
                "domain": analysis.get("domain", "general"),
                "strategy": analysis.get("strategy", "parallel")
            },
            recommendations=analysis.get("agents_needed", ["Domain Specialist", "Web Harvester"]),
            priority_aspects=analysis.get("key_aspects", [])
        )
        
        # Phase 2: Coordinated Agent Execution
        findings = {}
        agents_requested = analysis.get("agents_needed", ["Domain Specialist", "Web Harvester"])
        
        # Force all agents in expert mode
        if mode == "expert":
            agents_requested = ["Domain Specialist", "Web Harvester", "Fact Validator", "Quality Auditor"]
            logger.info("Expert mode: Engaging all agents for comprehensive analysis")
        
        # Calculate optimal execution order
        execution_levels = self.coordinator.calculate_execution_order(agents_requested)
        
        for level in execution_levels:
            # Execute agents in parallel within each level
            level_tasks = []
            
            for agent_name in level:
                # Check if agent should be skipped
                if self.coordinator.should_skip_agent(agent_name):
                    continue
                    
                # Create agent-specific handoff
                await self.communication.agent_handoff(AgentHandoff(
                    from_agent="Principal Synthesizer",
                    to_agent=agent_name,
                    query=query,
                    key_findings=analysis_handoff.key_findings,
                    priority_aspects=analysis_handoff.priority_aspects
                ))
                
                # Add agent task
                if agent_name == "Domain Specialist":
                    level_tasks.append(self._run_domain_specialist_enhanced(query, analysis, stream_callback))
                elif agent_name == "Web Harvester":
                    level_tasks.append(self._run_web_harvester_enhanced(query, analysis, stream_callback))
                elif agent_name == "Fact Validator":
                    level_tasks.append(self._run_fact_validator_enhanced(query, findings, stream_callback))
                elif agent_name == "Quality Auditor":
                    # Quality Auditor runs after synthesis, so skip here
                    continue
                    
            # Execute level in parallel
            if level_tasks:
                results = await asyncio.gather(*level_tasks, return_exceptions=True)
                
                # Process results
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"Agent failed: {result}")
                    elif isinstance(result, tuple) and len(result) == 2:
                        agent_name, agent_result = result
                        findings[agent_name] = agent_result
                        
                        # Record execution
                        self.health_monitor.record_execution(
                            agent_name,
                            success=True,
                            execution_time=time.time() - start_time,
                            tokens=len(agent_result.split())
                        )
                        
        # Phase 3: Enhanced Synthesis
        if stream_callback:
            await stream_callback({
                "type": "agent_start",
                "agent": "Principal Synthesizer",
                "message": "Synthesizing findings with quality optimization"
            })
            
        # Pass findings context to Principal
        synthesis_handoff = AgentHandoff(
            from_agent="Multiple Agents",
            to_agent="Principal Synthesizer",
            query=query,
            key_findings={"agents_contributed": list(findings.keys())},
            confidence=0.9 if len(findings) >= 2 else 0.7
        )
        await self.communication.agent_handoff(synthesis_handoff)
        
        # Get websites from context
        websites = self.communication.get_global_context("websites_explored") or []
        
        # Access wrapped agent if needed
        if hasattr(self.principal, 'agent'):
            final_report = await self.principal.agent.synthesize_findings(query, findings, stream_callback, websites)
        else:
            final_report = await self.principal.synthesize_findings(query, findings, stream_callback, websites)
        
        if stream_callback:
            await stream_callback({
                "type": "agent_complete",
                "agent": "Principal Synthesizer"
            })
            
        # Phase 4: Quality Assessment (if requested)
        quality_score = None
        if mode == "expert" and "Quality Auditor" in agents_requested:
            if stream_callback:
                await stream_callback({
                    "type": "agent_start",
                    "agent": "Quality Auditor",
                    "message": "Performing quality audit"
                })
                
            quality_score = await self.quality_auditor.agent.audit(final_report, stream_callback)
            
            if stream_callback:
                await stream_callback({
                    "type": "agent_complete",
                    "agent": "Quality Auditor"
                })
                
        # Store successful interaction in memory
        total_time = time.time() - start_time
        memory_entry = MemoryEntry(
            agent_name="orchestrator",
            query=query,
            response=final_report,
            prompt="",  # Complex multi-agent prompt
            metadata={
                "mode": mode,
                "agents_used": list(findings.keys()),
                "quality_score": quality_score,
                "complexity": analysis.get("complexity", "unknown"),
                "domain": analysis.get("domain", "general")
            },
            success=True,
            execution_time=total_time,
            tokens_used=sum(len(f.split()) for f in findings.values())
        )
        self.memory_system.store_interaction(memory_entry)
        logger.info(f"💾 CACHING: Stored successful interaction for future use")
        logger.info(f"   Query: '{query[:50]}...'")
        logger.info(f"   Quality score: {quality_score}")
        logger.info(f"   Execution time: {total_time:.1f}s")
        
        # Return enhanced result
        return {
            "query": query,
            "analysis": analysis,
            "agents_used": list(findings.keys()),
            "findings": findings,
            "synthesis": final_report,
            "quality_score": quality_score,
            "execution_time": round(total_time, 1),
            "total_tokens": sum(len(f.split()) for f in findings.values()) + len(final_report.split()),
            "timestamp": datetime.now().isoformat(),
            "performance_metrics": {
                agent: self.health_monitor.get_agent_health(agent)
                for agent in findings.keys()
            },
            "communication_summary": self.communication.get_conversation_summary(),
            "cache_stats": self.prompt_cache.get_cache_stats()
        }
        
    async def _run_domain_specialist_enhanced(self, query: str, analysis: Dict[str, Any], 
                                            callback) -> tuple:
        """Run domain specialist with enhancements"""
        if callback:
            await callback({
                "type": "agent_start",
                "agent": "Domain Specialist",
                "message": f"Analyzing {analysis.get('domain', 'general')} domain"
            })
            
        # Get context from communication protocol
        context = self.communication.build_agent_prompt_context("Domain Specialist")
        
        # Build enhanced prompt
        enhanced_prompt = self.prompt_builder.build_prompt(
            "Domain Specialist",
            "expert",
            f"Query: {query}\nDomain: {analysis.get('domain', 'general')}",
            {
                "previous_context": context,
                "priority_aspects": analysis.get("key_aspects", []),
                "user_expertise": "intermediate"  # Could be dynamic
            }
        )
        
        start = time.time()
        result = await self.domain_specialist.run_with_resilience(
            enhanced_prompt,
            callback,
            validation_fn=lambda r: len(r) > 100  # Simple validation
        )
        
        # Record performance
        self.health_monitor.record_execution(
            "Domain Specialist",
            success=True,
            execution_time=time.time() - start,
            tokens=len(result.split())
        )
        
        if callback:
            await callback({
                "type": "agent_complete",
                "agent": "Domain Specialist"
            })
            
        return ("Domain Specialist", result)
        
    async def _run_web_harvester_enhanced(self, query: str, analysis: Dict[str, Any], 
                                         callback) -> tuple:
        """Run web harvester with enhancements"""
        if callback:
            await callback({
                "type": "agent_start",
                "agent": "Web Harvester",
                "message": "Searching for current information"
            })
            
        aspects = analysis.get("key_aspects", ["current information", "recent updates"])
        
        start = time.time()
        result = await self.web_harvester.agent.search(query, aspects, callback)
        
        # Handle new response format
        if isinstance(result, dict):
            content = result.get("content", "")
            websites = result.get("websites_explored", [])
            # Store websites for later use
            self.communication.set_global_context("websites_explored", websites)
        else:
            # Backward compatibility
            content = result
            websites = []
        
        self.health_monitor.record_execution(
            "Web Harvester",
            success=True,
            execution_time=time.time() - start,
            tokens=len(content.split())
        )
        
        if callback:
            await callback({
                "type": "agent_complete",
                "agent": "Web Harvester"
            })
            
        return ("Web Harvester", content)
        
    async def _run_fact_validator_enhanced(self, query: str, findings: Dict[str, str], 
                                          callback) -> tuple:
        """Run fact validator with context from other agents"""
        if callback:
            await callback({
                "type": "agent_start",
                "agent": "Fact Validator",
                "message": "Validating findings"
            })
            
        # Combine findings for validation
        combined = " ".join(findings.values())[:2000]  # Limit context
        
        start = time.time()
        result = await self.fact_validator.agent.validate(combined, callback)
        
        self.health_monitor.record_execution(
            "Fact Validator",
            success=True,
            execution_time=time.time() - start,
            tokens=len(result.split())
        )
        
        if callback:
            await callback({
                "type": "agent_complete",
                "agent": "Fact Validator"
            })
            
        return ("Fact Validator", result)
        
    def _format_memory_response(self, memory: MemoryEntry) -> Dict[str, Any]:
        """Format a memory entry as a research response"""
        return {
            "query": memory.query,
            "synthesis": memory.response,
            "from_cache": True,
            "original_timestamp": memory.timestamp.isoformat(),
            "agents_used": memory.metadata.get("agents_used", []),
            "quality_score": memory.metadata.get("quality_score"),
            "execution_time": 0.1  # Near instant from cache
        }
        
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        return {
            "agents": {
                "Principal Synthesizer": self.health_monitor.get_agent_health("Principal Synthesizer"),
                "Domain Specialist": self.health_monitor.get_agent_health("Domain Specialist"),
                "Web Harvester": self.health_monitor.get_agent_health("Web Harvester"),
                "Fact Validator": self.health_monitor.get_agent_health("Fact Validator"),
                "Quality Auditor": self.health_monitor.get_agent_health("Quality Auditor")
            },
            "memory_system": {
                "total_memories": len(self.memory_system.cache.get("recent_queries", {})),
                "cache_performance": self.prompt_cache.get_cache_stats()
            },
            "communication": self.communication.get_conversation_summary()
        }