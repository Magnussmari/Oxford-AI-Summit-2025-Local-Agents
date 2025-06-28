"""
Agent communication protocol for context sharing and coordination
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
import json
from loguru import logger


@dataclass
class AgentHandoff:
    """Structured handoff package between agents"""
    from_agent: str
    to_agent: str
    timestamp: datetime = field(default_factory=datetime.now)
    query: str = ""
    key_findings: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    confidence: float = 0.8
    context: Dict[str, Any] = field(default_factory=dict)
    priority_aspects: List[str] = field(default_factory=list)
    
    def to_prompt_context(self) -> str:
        """Convert handoff to prompt context"""
        context_parts = [
            f"Previous agent: {self.from_agent}",
            f"Confidence level: {self.confidence}"
        ]
        
        if self.key_findings:
            findings_str = "\n".join(f"- {k}: {v}" for k, v in self.key_findings.items())
            context_parts.append(f"Key findings:\n{findings_str}")
            
        if self.recommendations:
            rec_str = "\n".join(f"- {r}" for r in self.recommendations)
            context_parts.append(f"Recommendations:\n{rec_str}")
            
        if self.warnings:
            warn_str = "\n".join(f"- {w}" for w in self.warnings)
            context_parts.append(f"Warnings:\n{warn_str}")
            
        if self.priority_aspects:
            context_parts.append(f"Priority aspects to investigate: {', '.join(self.priority_aspects)}")
            
        return "\n\n".join(context_parts)


class AgentCommunicationProtocol:
    """Enable agents to share context and learnings"""
    
    def __init__(self):
        self.shared_context: Dict[str, AgentHandoff] = {}
        self.agent_insights: Dict[str, List[Dict]] = {}
        self.conversation_history: List[Dict] = []
        self.global_context: Dict[str, Any] = {}
        
    async def agent_handoff(self, handoff: AgentHandoff):
        """Process structured handoff between agents"""
        # Validate handoff
        if not handoff.from_agent or not handoff.to_agent:
            logger.warning("Invalid handoff: missing agent names")
            return
            
        # Store handoff
        self.shared_context[handoff.to_agent] = handoff
        
        # Log handoff
        logger.info(f"Handoff from {handoff.from_agent} to {handoff.to_agent}")
        
        # Update conversation history
        self.conversation_history.append({
            "type": "handoff",
            "timestamp": handoff.timestamp.isoformat(),
            "from": handoff.from_agent,
            "to": handoff.to_agent,
            "findings_count": len(handoff.key_findings),
            "confidence": handoff.confidence
        })
        
    def get_agent_context(self, agent_name: str) -> Optional[AgentHandoff]:
        """Retrieve context for an agent"""
        return self.shared_context.get(agent_name)
        
    def add_agent_insight(self, agent_name: str, insight: Dict[str, Any]):
        """Add an insight from an agent for future reference"""
        if agent_name not in self.agent_insights:
            self.agent_insights[agent_name] = []
            
        insight["timestamp"] = datetime.now().isoformat()
        self.agent_insights[agent_name].append(insight)
        
        # Keep only recent insights (last 100)
        if len(self.agent_insights[agent_name]) > 100:
            self.agent_insights[agent_name] = self.agent_insights[agent_name][-100:]
            
    def get_agent_insights(self, agent_name: str, topic: str = None) -> List[Dict]:
        """Get insights from an agent, optionally filtered by topic"""
        insights = self.agent_insights.get(agent_name, [])
        
        if topic:
            # Simple topic filtering
            filtered = []
            for insight in insights:
                if topic.lower() in str(insight).lower():
                    filtered.append(insight)
            return filtered
            
        return insights
        
    def set_global_context(self, key: str, value: Any):
        """Set global context available to all agents"""
        self.global_context[key] = value
        
    def get_global_context(self, key: str = None) -> Any:
        """Get global context"""
        if key:
            return self.global_context.get(key)
        return self.global_context
        
    def build_agent_prompt_context(self, agent_name: str) -> str:
        """Build complete context for an agent's prompt"""
        context_parts = []
        
        # Add handoff context if available
        handoff = self.get_agent_context(agent_name)
        if handoff:
            context_parts.append("=== Previous Agent Context ===")
            context_parts.append(handoff.to_prompt_context())
            
        # Add relevant global context
        if self.global_context:
            context_parts.append("=== Global Context ===")
            for key, value in self.global_context.items():
                if isinstance(value, (str, int, float, bool)):
                    context_parts.append(f"{key}: {value}")
                    
        # Add recent conversation summary
        if len(self.conversation_history) > 0:
            recent = self.conversation_history[-5:]  # Last 5 events
            context_parts.append("=== Recent Activity ===")
            for event in recent:
                if event["type"] == "handoff":
                    context_parts.append(
                        f"- {event['from']} → {event['to']} (confidence: {event['confidence']})"
                    )
                    
        return "\n\n".join(context_parts) if context_parts else ""
        
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the conversation"""
        if not self.conversation_history:
            return {"status": "no_conversation"}
            
        handoffs = [e for e in self.conversation_history if e["type"] == "handoff"]
        
        return {
            "total_handoffs": len(handoffs),
            "agents_involved": list(set(
                [h["from"] for h in handoffs] + [h["to"] for h in handoffs]
            )),
            "average_confidence": sum(h["confidence"] for h in handoffs) / len(handoffs) if handoffs else 0,
            "conversation_length": len(self.conversation_history)
        }


class AgentCoordinator:
    """Coordinate agent activities and dependencies"""
    
    def __init__(self, communication_protocol: AgentCommunicationProtocol):
        self.protocol = communication_protocol
        self.agent_dependencies: Dict[str, List[str]] = {}
        self.execution_order: List[str] = []
        
    def set_dependencies(self, agent_name: str, depends_on: List[str]):
        """Set agent dependencies"""
        self.agent_dependencies[agent_name] = depends_on
        
    def calculate_execution_order(self, requested_agents: List[str]) -> List[List[str]]:
        """Calculate optimal execution order considering dependencies"""
        # Build dependency graph
        graph = {}
        for agent in requested_agents:
            graph[agent] = self.agent_dependencies.get(agent, [])
            
        # Topological sort to find execution order
        visited = set()
        stack = []
        
        def visit(agent):
            if agent in visited:
                return
            visited.add(agent)
            for dep in graph.get(agent, []):
                if dep in requested_agents:
                    visit(dep)
            stack.append(agent)
            
        for agent in requested_agents:
            visit(agent)
            
        # Group by levels for parallel execution
        levels = []
        positioned = set()
        
        while stack:
            level = []
            for agent in stack[:]:
                deps = graph.get(agent, [])
                if all(dep in positioned or dep not in requested_agents for dep in deps):
                    level.append(agent)
                    stack.remove(agent)
                    positioned.add(agent)
            if level:
                levels.append(level)
                
        return levels
        
    def should_skip_agent(self, agent_name: str) -> bool:
        """Check if an agent should be skipped based on previous results"""
        handoff = self.protocol.get_agent_context(agent_name)
        
        if handoff and handoff.warnings:
            # Check for skip signals
            for warning in handoff.warnings:
                if "skip" in warning.lower() or "not needed" in warning.lower():
                    logger.info(f"Skipping {agent_name} based on previous agent recommendation")
                    return True
                    
        return False


class MessageBus:
    """Simple message bus for agent events"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[callable]] = {}
        
    def subscribe(self, event_type: str, handler: callable):
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        
    async def publish(self, event_type: str, data: Any):
        """Publish an event"""
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")
                    
    def unsubscribe(self, event_type: str, handler: callable):
        """Unsubscribe from an event type"""
        if event_type in self.subscribers and handler in self.subscribers[event_type]:
            self.subscribers[event_type].remove(handler)