"""
Few-shot examples for consistent agent outputs
"""

from typing import List, Dict, Any
from dataclasses import dataclass
import json


@dataclass
class FewShotExample:
    """Single few-shot example"""
    query: str
    response: Any
    explanation: str = ""
    complexity: str = "moderate"
    

class AgentExamples:
    """Curated examples for each agent type"""
    
    @staticmethod
    def get_principal_examples() -> List[Dict[str, Any]]:
        """Examples for Principal Synthesizer analysis"""
        return [
            {
                "query": "What is quantum computing?",
                "response": {
                    "complexity": "simple",
                    "reasoning": "Single concept explanation with established knowledge",
                    "domain": "technology",
                    "subdomain": "quantum physics/computer science",
                    "agents_needed": ["Web Harvester"],
                    "agent_rationale": {
                        "Web Harvester": "To get current, accessible explanations"
                    },
                    "strategy": "sequential",
                    "strategy_explanation": "Single agent can handle this query",
                    "key_aspects": ["basic definition", "key principles", "simple examples"],
                    "expected_challenges": ["Technical jargon simplification"],
                    "success_criteria": ["Clear explanation", "Practical examples"]
                }
            },
            {
                "query": "Compare the environmental impact of electric vs hydrogen vehicles including lifecycle analysis",
                "response": {
                    "complexity": "complex",
                    "reasoning": "Multi-faceted comparison requiring technical analysis and current data",
                    "domain": "technology",
                    "subdomain": "sustainable transportation",
                    "agents_needed": ["Domain Specialist", "Web Harvester", "Fact Validator"],
                    "agent_rationale": {
                        "Domain Specialist": "Deep technical analysis of both technologies",
                        "Web Harvester": "Current studies and lifecycle data",
                        "Fact Validator": "Verify environmental claims and statistics"
                    },
                    "strategy": "hybrid",
                    "strategy_explanation": "Domain analysis first, then parallel web search and validation",
                    "key_aspects": ["lifecycle emissions", "manufacturing impact", "infrastructure requirements", "energy sources"],
                    "expected_challenges": ["Conflicting studies", "Rapidly changing technology"],
                    "success_criteria": ["Balanced comparison", "Cited sources", "Quantitative data"]
                }
            },
            {
                "query": "How do I make chocolate chip cookies?",
                "response": {
                    "complexity": "simple",
                    "reasoning": "Common knowledge request, single straightforward answer",
                    "domain": "general",
                    "subdomain": "cooking/recipes",
                    "agents_needed": ["Web Harvester"],
                    "agent_rationale": {
                        "Web Harvester": "Find popular, tested recipes"
                    },
                    "strategy": "sequential",
                    "strategy_explanation": "Single source sufficient for recipe",
                    "key_aspects": ["ingredients", "steps", "tips"],
                    "expected_challenges": ["None significant"],
                    "success_criteria": ["Complete recipe", "Clear instructions"]
                }
            }
        ]
    
    @staticmethod
    def get_domain_specialist_examples() -> List[Dict[str, Any]]:
        """Examples for Domain Specialist"""
        return [
            {
                "query": "Explain CRISPR gene editing",
                "domain": "biotechnology",
                "response": """CRISPR-Cas9 is a revolutionary gene-editing technology that allows precise modification of DNA sequences. 

**Key Components:**
- **CRISPR**: Clustered Regularly Interspaced Short Palindromic Repeats
- **Cas9**: An enzyme that acts as molecular scissors
- **Guide RNA**: Directs Cas9 to specific DNA locations

**How it works:**
1. Guide RNA identifies target DNA sequence
2. Cas9 enzyme cuts DNA at precise location
3. Cell's repair mechanisms can delete genes or insert new ones

**Applications:**
- Disease treatment (sickle cell, cancer)
- Agricultural improvements
- Basic research

**Current limitations:**
- Off-target effects
- Delivery challenges
- Ethical considerations"""
            }
        ]
    
    @staticmethod
    def get_synthesis_examples() -> List[Dict[str, Any]]:
        """Examples for synthesis tasks"""
        return [
            {
                "query": "What are the latest AI safety developments?",
                "findings": {
                    "Domain Specialist": "Constitutional AI and RLHF advances...",
                    "Web Harvester": "Recent papers on alignment research...",
                    "Fact Validator": "Verified claims about safety measures..."
                },
                "response": """# Executive Summary
Recent AI safety developments focus on Constitutional AI, improved RLHF techniques, and interpretability research, with major labs implementing concrete safety measures.

## Key Findings
- **Constitutional AI**: Anthropic's method showing promise for self-supervised safety
- **Interpretability advances**: New techniques for understanding model internals
- **Industry coordination**: Major labs forming safety commitments

## Conclusions
AI safety is progressing from theoretical concerns to practical implementations, though significant challenges remain in alignment and robustness."""
            }
        ]
    
    @staticmethod
    def format_examples_for_prompt(examples: List[Dict[str, Any]], 
                                  example_type: str = "analysis") -> str:
        """Format examples for inclusion in prompts"""
        formatted = []
        
        for i, example in enumerate(examples, 1):
            if example_type == "analysis":
                formatted.append(f"Example {i}:")
                formatted.append(f"Query: {example['query']}")
                formatted.append(f"Analysis: {json.dumps(example['response'], indent=2)}")
                formatted.append("")
            elif example_type == "response":
                formatted.append(f"Example {i}:")
                formatted.append(f"Query: {example['query']}")
                if 'domain' in example:
                    formatted.append(f"Domain: {example['domain']}")
                formatted.append(f"Response:\n{example['response']}")
                formatted.append("")
                
        return '\n'.join(formatted)


class ExampleSelector:
    """Select most relevant examples based on query similarity"""
    
    def __init__(self):
        self.examples_cache = {
            "principal": AgentExamples.get_principal_examples(),
            "domain": AgentExamples.get_domain_specialist_examples(),
            "synthesis": AgentExamples.get_synthesis_examples()
        }
        
    def get_relevant_examples(self, query: str, agent_type: str, 
                            max_examples: int = 2) -> List[Dict[str, Any]]:
        """Get most relevant examples for a query"""
        all_examples = self.examples_cache.get(agent_type, [])
        
        if not all_examples:
            return []
            
        # Simple relevance scoring based on keyword overlap
        scored_examples = []
        query_words = set(query.lower().split())
        
        for example in all_examples:
            example_words = set(example['query'].lower().split())
            # Score based on word overlap
            overlap = len(query_words & example_words)
            score = overlap / max(len(query_words), 1)
            scored_examples.append((score, example))
            
        # Sort by score and return top examples
        scored_examples.sort(key=lambda x: x[0], reverse=True)
        return [ex[1] for ex in scored_examples[:max_examples]]
    
    def get_complexity_matched_examples(self, complexity: str, 
                                      agent_type: str) -> List[Dict[str, Any]]:
        """Get examples matching a specific complexity level"""
        all_examples = self.examples_cache.get(agent_type, [])
        
        matched = []
        for example in all_examples:
            if example.get('response', {}).get('complexity') == complexity:
                matched.append(example)
                
        return matched[:2]  # Return up to 2 examples


class PromptExampleBuilder:
    """Build example sections for prompts"""
    
    def __init__(self):
        self.selector = ExampleSelector()
        
    def build_examples_section(self, query: str, agent_type: str, 
                             include_complexity_match: bool = True) -> str:
        """Build a complete examples section for a prompt"""
        examples = []
        
        # Get query-relevant examples
        relevant = self.selector.get_relevant_examples(query, agent_type)
        examples.extend(relevant)
        
        # Optionally add complexity-matched examples
        if include_complexity_match and agent_type == "principal":
            # Try to guess complexity from query length and keywords
            complexity = self._estimate_complexity(query)
            complexity_matched = self.selector.get_complexity_matched_examples(
                complexity, agent_type
            )
            # Add only if not already included
            for ex in complexity_matched:
                if ex not in examples:
                    examples.append(ex)
                    
        # Format examples
        if examples:
            example_type = "analysis" if agent_type == "principal" else "response"
            return AgentExamples.format_examples_for_prompt(examples, example_type)
        else:
            return ""
            
    def _estimate_complexity(self, query: str) -> str:
        """Simple heuristic to estimate query complexity"""
        word_count = len(query.split())
        
        # Check for complexity indicators
        complex_keywords = ["compare", "analyze", "evaluate", "impact", "versus", 
                          "lifecycle", "comprehensive", "detailed"]
        simple_keywords = ["what is", "define", "how to", "explain"]
        
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in simple_keywords):
            return "simple"
        elif any(keyword in query_lower for keyword in complex_keywords) or word_count > 20:
            return "complex"
        else:
            return "moderate"