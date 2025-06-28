"""
Structured prompting system for consistent, high-quality agent outputs
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
import json


@dataclass
class PromptTemplate:
    """Structured prompt template with clear sections"""
    
    role: str
    expertise: str
    context: Dict[str, Any]
    task: str
    constraints: Dict[str, Any]
    examples: Optional[List[Dict]] = None
    output_format: Optional[str] = None
    
    def render(self, **kwargs) -> str:
        """Render the template with provided values"""
        template = f"""<role>
You are {self.role}, part of the LocalMind Collective multi-agent system.
Your expertise: {self.expertise}
Current date: {datetime.now().strftime("%B %d, %Y")}
</role>

<context>
{self._render_context()}
</context>

<task>
{self.task}
</task>

<constraints>
{self._render_constraints()}
</constraints>"""

        if self.examples:
            template += f"\n\n<examples>\n{self._render_examples()}\n</examples>"
            
        if kwargs.get('query'):
            template += f"\n\n<query>\n{kwargs['query']}\n</query>"
            
        if self.output_format:
            template += f"\n\n<output_format>\n{self.output_format}\n</output_format>"
            
        return template
    
    def _render_context(self) -> str:
        """Render context section"""
        lines = []
        for key, value in self.context.items():
            if isinstance(value, list):
                lines.append(f"{key}: {', '.join(str(v) for v in value)}")
            else:
                lines.append(f"{key}: {value}")
        return '\n'.join(lines)
    
    def _render_constraints(self) -> str:
        """Render constraints section"""
        lines = []
        for key, value in self.constraints.items():
            lines.append(f"- {key}: {value}")
        return '\n'.join(lines)
    
    def _render_examples(self) -> str:
        """Render examples section"""
        examples_text = []
        for i, example in enumerate(self.examples, 1):
            examples_text.append(f"Example {i}:")
            examples_text.append(f"Query: {example.get('query', 'N/A')}")
            examples_text.append(f"Response: {json.dumps(example.get('response', {}), indent=2)}")
            examples_text.append("")
        return '\n'.join(examples_text)


class StructuredPrompt:
    """Advanced structured prompting with validation and optimization"""
    
    @staticmethod
    def create_analysis_prompt(agent_name: str, query: str, examples: List[Dict] = None) -> str:
        """Create a structured analysis prompt"""
        template = PromptTemplate(
            role=f"{agent_name} Analyst",
            expertise="query analysis and multi-agent orchestration",
            context={
                "system_state": "ready",
                "available_agents": ["Domain Specialist", "Web Harvester", "Fact Validator", "Quality Auditor"],
                "processing_modes": ["simple", "moderate", "complex"]
            },
            task="Analyze the given query to determine optimal processing strategy",
            constraints={
                "response_format": "JSON",
                "max_analysis_time": "30 seconds",
                "focus_areas": "complexity assessment, domain identification, agent selection",
                "avoid": "over-complication, unnecessary agents"
            },
            examples=examples or [],
            output_format="""{
    "complexity": "simple|moderate|complex",
    "reasoning": "Brief explanation of complexity assessment",
    "domain": "primary domain (technology|science|business|health|general)",
    "subdomain": "specific area if applicable",
    "agents_needed": ["Agent Name 1", "Agent Name 2"],
    "agent_rationale": {
        "Agent Name 1": "Why this agent is needed",
        "Agent Name 2": "Why this agent is needed"
    },
    "strategy": "parallel|sequential|hybrid",
    "strategy_explanation": "Why this execution strategy",
    "key_aspects": ["aspect 1", "aspect 2", "aspect 3"],
    "expected_challenges": ["potential issue 1", "potential issue 2"],
    "success_criteria": ["criterion 1", "criterion 2"]
}"""
        )
        
        return template.render(query=query)
    
    @staticmethod
    def create_synthesis_prompt(agent_name: str, query: str, findings: Dict[str, str], 
                              max_length: int = 500) -> str:
        """Create a structured synthesis prompt"""
        template = PromptTemplate(
            role=f"{agent_name} Synthesizer",
            expertise="information synthesis and report generation",
            context={
                "original_query": query,
                "contributing_agents": list(findings.keys()),
                "synthesis_goal": "coherent, actionable report"
            },
            task="Synthesize findings from multiple agents into a unified report",
            constraints={
                "response_format": "Markdown",
                "max_length": f"{max_length} words",
                "structure": "executive summary, key findings, conclusions",
                "tone": "professional, clear, concise"
            },
            output_format="""# Executive Summary
Brief overview of findings (2-3 sentences)

## Key Findings
- Finding 1
- Finding 2
- Finding 3

## Conclusions
Actionable insights and recommendations"""
        )
        
        # Add findings to context
        findings_text = "\n\n".join(
            f"### {agent}\n{content[:500]}" for agent, content in findings.items()
        )
        
        return template.render(query=query) + f"\n\n<agent_findings>\n{findings_text}\n</agent_findings>"
    
    @staticmethod
    def create_cot_prompt(agent_name: str, query: str, thinking_steps: List[str]) -> str:
        """Create a Chain-of-Thought prompt"""
        thinking_process = '\n'.join(f"{i}. {step}" for i, step in enumerate(thinking_steps, 1))
        
        template = f"""<thinking_process>
Let me analyze this step by step:

{thinking_process}
</thinking_process>

Query: {query}

Now, following the thinking process above, let me work through each step:
"""
        
        for i, step in enumerate(thinking_steps, 1):
            template += f"\n\nStep {i} - {step}:\n[Analyze this step]"
            
        return template


class PromptValidator:
    """Validate and improve prompts"""
    
    @staticmethod
    def validate_json_response(response: str) -> Optional[Dict]:
        """Extract and validate JSON from response"""
        import re
        
        # Try to find JSON in various formats
        json_patterns = [
            r'\{[^{}]*\}',  # Simple JSON
            r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}',  # Nested JSON
            r'```json\s*(.*?)\s*```',  # Markdown code block
            r'```\s*(.*?)\s*```'  # Generic code block
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            for match in matches:
                try:
                    # Clean up the match
                    if isinstance(match, tuple):
                        match = match[0]
                    match = match.strip()
                    
                    # Try to parse as JSON
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
                    
        return None
    
    @staticmethod
    def clean_response(response: str, remove_thinking: bool = True) -> str:
        """Clean up response text while preserving markdown structure"""
        import re
        
        # Remove thinking tags if present
        if remove_thinking:
            # Remove <think> or <thinking> blocks
            response = re.sub(r'<think[^>]*>.*?</think>', '', response, flags=re.DOTALL)
            response = re.sub(r'<thinking[^>]*>.*?</thinking>', '', response, flags=re.DOTALL)
            
        lines = response.split('\n')
        cleaned_lines = []
        skip_thinking = False
        in_code_block = False
        
        for line in lines:
            # Track code blocks to not process their content
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                cleaned_lines.append(line)
                continue
                
            # Skip thinking/meta-commentary if requested (but not in code blocks)
            if not in_code_block and remove_thinking and any(phrase in line.lower() for phrase in 
                                     ['okay,', 'i need to', 'looking at', 'let me', 'first,', 
                                      'i\'ll', 'i am', 'i will', 'now i', 'based on']):
                skip_thinking = True
                # Check if this line also has content
                if any(marker in line for marker in ['#', '**', '-', '*', '1.', '2.', '3.']):
                    # Extract the content part
                    for marker in ['#', '**', '-', '*']:
                        if marker in line:
                            idx = line.find(marker)
                            if idx > 0:
                                line = line[idx:]
                                skip_thinking = False
                                break
                            
            # Reset skip flag on actual content markers
            if skip_thinking and (line.startswith('#') or line.startswith('**') or 
                                 line.strip().startswith('-') or line.strip().startswith('*') or
                                 line.strip().startswith('1.') or line.strip() == ''):
                skip_thinking = False
                
            if not skip_thinking or in_code_block:
                cleaned_lines.append(line)
                
        # Post-process to ensure good markdown structure
        result = '\n'.join(cleaned_lines).strip()
        
        # Ensure proper spacing around headers
        result = re.sub(r'\n(#{1,6})', r'\n\n\1', result)
        result = re.sub(r'(#{1,6}[^\n]+)\n(?!\n)', r'\1\n\n', result)
        
        # Remove multiple blank lines
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        return result.strip()


class PromptOptimizer:
    """Optimize prompts for better performance"""
    
    @staticmethod
    def compress_prompt(prompt: str) -> str:
        """Compress prompt while maintaining clarity"""
        # Remove excessive whitespace
        prompt = ' '.join(prompt.split())
        
        # Common abbreviations
        replacements = {
            "artificial intelligence": "AI",
            "machine learning": "ML", 
            "large language model": "LLM",
            "natural language processing": "NLP",
            "for example": "e.g.",
            "that is": "i.e.",
            "et cetera": "etc."
        }
        
        for full, abbr in replacements.items():
            prompt = prompt.replace(full, abbr)
            prompt = prompt.replace(full.title(), abbr)
            
        return prompt
    
    @staticmethod
    def add_format_enforcement(prompt: str, format_type: str = "json") -> str:
        """Add format enforcement to prompt"""
        enforcement = {
            "json": "\n\nIMPORTANT: Respond ONLY with valid JSON. No additional text or explanation.",
            "markdown": "\n\nIMPORTANT: Format your response in clean Markdown. Start directly with the content.",
            "list": "\n\nIMPORTANT: Respond with a numbered list. No additional commentary.",
            "boolean": "\n\nIMPORTANT: Respond with only 'true' or 'false'."
        }
        
        return prompt + enforcement.get(format_type, "")