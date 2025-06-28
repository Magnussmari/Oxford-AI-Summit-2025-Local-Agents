"""
Enhanced Principal Synthesizer with structured prompting and CoT
"""

import json
import re
from typing import Dict, Any, List
from loguru import logger

from .base import PresentationAgent, CURRENT_DATE
from .core.prompting import StructuredPrompt, PromptValidator
from .core.examples import AgentExamples
from .core.resilience import ResilientAgentWrapper


class ImprovedPrincipalSynthesizer(PresentationAgent):
    """Enhanced Principal Synthesizer with structured prompting and Chain-of-Thought reasoning."""
    
    def __init__(self):
        super().__init__(
            name="Principal Synthesizer",
            model="deepseek-r1:8b",
            role="orchestrator",
            temperature=0.1
        )
        self.timeout = 360  # 6 minutes for deep reasoning
        self.validator = PromptValidator()
        self.examples = AgentExamples.get_principal_examples()
        
    async def analyze_query(self, query: str, stream_callback=None) -> Dict[str, Any]:
        """Analyze query with structured prompting and CoT reasoning."""
        
        # Build structured prompt with examples
        prompt = StructuredPrompt.create_analysis_prompt(
            agent_name=self.name,
            query=query,
            examples=self.examples
        )
        
        # Add Chain-of-Thought reasoning
        cot_prompt = self._add_cot_reasoning(prompt, query)
        
        # Run with context for optimization
        context = {
            "query_type": "analytical",
            "response_format": "json",
            "include_examples": True,
            "max_tokens": 2000
        }
        
        response = await self.run(cot_prompt, stream_callback, context)
        
        # Validate and extract JSON
        result = self.validator.validate_json_response(response)
        
        if result:
            # Validate required fields
            if self._validate_analysis_result(result):
                return result
            else:
                logger.warning("Invalid analysis structure, using enhanced fallback")
                return self._create_enhanced_fallback(query, result)
        else:
            logger.error("Failed to parse analysis response")
            return self._create_enhanced_fallback(query)
            
    def _add_cot_reasoning(self, base_prompt: str, query: str) -> str:
        """Add Chain-of-Thought reasoning to prompt"""
        cot_section = f"""
<thinking_process>
For the query "{query}", I need to analyze step by step:

1. **Topic Identification**: What is the core subject matter? Is it asking for information, comparison, analysis, or creation?

2. **Complexity Assessment**:
   - Simple: Single concept, straightforward answer, common knowledge
   - Moderate: Multiple related concepts, some analysis needed, current information helpful
   - Complex: Multi-faceted analysis, conflicting information possible, deep expertise required

3. **Domain Classification**: Which field of knowledge does this primarily belong to?
   - Technology: Computing, AI, software, hardware, internet
   - Science: Physics, chemistry, biology, medicine, research
   - Business: Economics, finance, management, marketing
   - Health: Medical, wellness, nutrition, mental health
   - General: Everyday topics, how-to guides, common knowledge

4. **Agent Selection Logic**:
   - Domain Specialist: Needed for deep technical analysis or expert knowledge
   - Web Harvester: Needed for current events, recent developments, or varied perspectives
   - Fact Validator: Needed when claims need verification or conflicting information exists
   - Quality Auditor: Needed for complex outputs requiring quality assessment

5. **Execution Strategy**:
   - Sequential: When one agent's output informs another's input
   - Parallel: When agents can work independently
   - Hybrid: Mix of both for optimal efficiency

Now let me apply this thinking to the specific query...
</thinking_process>

{base_prompt}"""
        
        return cot_section
        
    def _validate_analysis_result(self, result: Dict[str, Any]) -> bool:
        """Validate that analysis result has all required fields"""
        required_fields = [
            "complexity", "domain", "agents_needed", 
            "strategy", "key_aspects"
        ]
        
        return all(field in result for field in required_fields)
        
    def _create_enhanced_fallback(self, query: str, partial_result: Dict = None) -> Dict[str, Any]:
        """Create an enhanced fallback response"""
        # Use any partial results we got
        base_fallback = {
            "complexity": "high",
            "reasoning": "Analysis required fallback - engaging all agents for comprehensive coverage",
            "domain": "general",
            "subdomain": "unspecified",
            "agents_needed": ["Domain Specialist", "Web Harvester", "Fact Validator", "Quality Auditor"],
            "agent_rationale": {
                "Domain Specialist": "Provide expert analysis on the topic",
                "Web Harvester": "Gather current information and perspectives from the web",
                "Fact Validator": "Verify claims and ensure accuracy",
                "Quality Auditor": "Assess completeness and quality of findings"
            },
            "strategy": "hybrid",
            "strategy_explanation": "Web and Domain work in parallel, then Fact Validator and Quality Auditor review",
            "key_aspects": self._extract_key_aspects(query),
            "expected_challenges": ["Complex analysis required", "Multiple perspectives needed"],
            "success_criteria": ["Complete information", "Verified facts", "High quality output"],
            "fallback": True
        }
        
        # Merge with any partial results
        if partial_result:
            for key, value in partial_result.items():
                if value and key in base_fallback:
                    base_fallback[key] = value
                    
        return base_fallback
        
    def _extract_key_aspects(self, query: str) -> List[str]:
        """Extract key aspects from query"""
        # Simple keyword extraction
        aspects = []
        
        # Common question words indicate aspects
        question_patterns = {
            "what": "definition and explanation",
            "how": "process or methodology",
            "why": "reasoning and causation",
            "when": "timeline and context",
            "where": "location and scope",
            "who": "people and organizations",
            "compare": "comparative analysis",
            "impact": "effects and consequences",
            "difference": "distinctions and contrasts"
        }
        
        query_lower = query.lower()
        for pattern, aspect in question_patterns.items():
            if pattern in query_lower:
                aspects.append(aspect)
                
        # Add topic-specific aspects
        if "vs" in query_lower or "versus" in query_lower:
            aspects.append("comparative analysis")
        if "future" in query_lower:
            aspects.append("predictions and trends")
        if "current" in query_lower or "latest" in query_lower:
            aspects.append("recent developments")
            
        # Default aspects if none found
        if not aspects:
            aspects = ["main topic", "key information", "practical applications"]
            
        return aspects[:5]  # Limit to 5 aspects
        
    async def synthesize_findings(self, query: str, findings: Dict[str, str], 
                                 stream_callback=None) -> str:
        """Enhanced synthesis with structured output"""
        
        # Build structured synthesis prompt
        prompt = StructuredPrompt.create_synthesis_prompt(
            agent_name=self.name,
            query=query,
            findings=findings,
            max_length=500
        )
        
        # Add synthesis instructions
        enhanced_prompt = f"""{prompt}

<synthesis_guidelines>
1. Start with the most important insight
2. Integrate findings from all agents seamlessly
3. Resolve any conflicts between agent responses
4. Highlight actionable conclusions
5. Keep language clear and accessible
</synthesis_guidelines>

Remember: This is for a live demonstration. Be concise but impactful."""
        
        # Run with optimization
        context = {
            "query_type": "synthesis",
            "response_format": "markdown",
            "compress_prompt": True,
            "max_tokens": 1500
        }
        
        response = await self.run(enhanced_prompt, stream_callback, context)
        
        # Clean up response
        cleaned = self.validator.clean_response(response, remove_thinking=True)
        
        # Ensure proper markdown structure
        if not cleaned.strip().startswith("#"):
            # Add proper heading based on query
            if "benefits" in query.lower() or "advantages" in query.lower():
                cleaned = f"# Benefits Analysis\n\n{cleaned}"
            elif "best practices" in query.lower():
                cleaned = f"# Best Practices Guide\n\n{cleaned}"
            elif "explain" in query.lower() or "what is" in query.lower():
                cleaned = f"# Explanation\n\n{cleaned}"
            else:
                cleaned = f"# Research Summary\n\n{cleaned}"
        
        # Ensure sections have proper headers
        import re
        # Look for common section patterns and ensure they're headers
        section_patterns = [
            (r'^(Key Benefits|Benefits|Advantages):?\s*$', '## Key Benefits'),
            (r'^(Best Practices|Practices|Guidelines):?\s*$', '## Best Practices'),
            (r'^(Conclusion|Summary|In Conclusion):?\s*$', '## Conclusion'),
            (r'^(Overview|Introduction):?\s*$', '## Overview'),
            (r'^(Challenges|Limitations|Drawbacks):?\s*$', '## Challenges'),
            (r'^(Implementation|Getting Started|Setup):?\s*$', '## Implementation'),
        ]
        
        lines = cleaned.split('\n')
        for i, line in enumerate(lines):
            for pattern, replacement in section_patterns:
                if re.match(pattern, line.strip(), re.IGNORECASE):
                    lines[i] = replacement
                    break
                    
        cleaned = '\n'.join(lines)
        
        # Ensure lists are properly formatted
        cleaned = re.sub(r'^(\d+)\.\s+', r'\1. ', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'^-\s+', r'- ', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'^\*\s+', r'* ', cleaned, flags=re.MULTILINE)
            
        return cleaned


class PrincipalSynthesizerWithResilience:
    """Principal Synthesizer wrapped with resilience patterns"""
    
    def __init__(self):
        self.agent = ImprovedPrincipalSynthesizer()
        self.wrapper = ResilientAgentWrapper(self.agent)
        
    async def analyze_query(self, query: str, stream_callback=None) -> Dict[str, Any]:
        """Analyze with resilience"""
        
        # Define validation function for analysis results
        def validate_analysis(response: str) -> bool:
            result = PromptValidator.validate_json_response(response)
            if not result:
                return False
            return all(field in result for field in ["complexity", "domain", "agents_needed"])
            
        # Run with resilience
        response = await self.wrapper.run_with_resilience(
            prompt=query,  # The analyze_query method will build the actual prompt
            stream_callback=stream_callback,
            validation_fn=validate_analysis
        )
        
        # Parse result
        result = PromptValidator.validate_json_response(response)
        if result:
            return result
        else:
            # Use fallback
            return self.agent._create_enhanced_fallback(query)
            
    async def synthesize_findings(self, query: str, findings: Dict[str, str], 
                                 stream_callback=None) -> str:
        """Synthesize with resilience"""
        
        # Simple validation - ensure we get markdown
        def validate_synthesis(response: str) -> bool:
            return len(response) > 50 and ("##" in response or "**" in response)
            
        return await self.wrapper.run_with_resilience(
            prompt=f"Query: {query}\nFindings: {findings}",  # Simplified for wrapper
            stream_callback=stream_callback,
            validation_fn=validate_synthesis
        )