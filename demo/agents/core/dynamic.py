"""
Dynamic components for adaptive agent behavior
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import hashlib
from dataclasses import dataclass
from loguru import logger
import math


class AdaptiveTemperatureController:
    """Dynamically adjust temperature based on context and performance"""
    
    def __init__(self):
        self.base_temperatures = {
            "orchestrator": 0.1,
            "expert": 0.2,
            "researcher": 0.3,
            "creative": 0.7,
            "validator": 0.1,
            "synthesizer": 0.2
        }
        self.performance_history = {}
        self.temperature_adjustments = {}
        
    def get_optimal_temperature(self, agent_name: str, agent_type: str, 
                              query_type: str, previous_attempts: int = 0,
                              performance_metrics: Dict = None) -> float:
        """Calculate optimal temperature for current context"""
        
        # Get base temperature
        base_temp = self.base_temperatures.get(agent_type, 0.3)
        
        # Adjust based on previous attempts (increase creativity if failing)
        if previous_attempts > 0:
            attempt_adjustment = min(0.2, 0.05 * previous_attempts)
            base_temp = min(0.9, base_temp + attempt_adjustment)
            logger.info(f"Increasing temperature for {agent_name} due to {previous_attempts} retries")
            
        # Adjust based on query type
        query_adjustments = {
            "factual": 0.7,      # More deterministic
            "analytical": 0.8,   # Somewhat deterministic
            "creative": 1.3,     # More creative
            "exploratory": 1.2,  # More exploratory
            "technical": 0.9     # Balanced
        }
        
        query_multiplier = query_adjustments.get(query_type, 1.0)
        adjusted_temp = base_temp * query_multiplier
        
        # Adjust based on recent performance
        if performance_metrics:
            success_rate = performance_metrics.get("success_rate", 1.0)
            if success_rate < 0.7:
                # Increase temperature if struggling
                adjusted_temp = min(0.9, adjusted_temp * 1.2)
            elif success_rate > 0.95:
                # Can afford to be more deterministic
                adjusted_temp = adjusted_temp * 0.9
                
        # Apply any manual adjustments
        if agent_name in self.temperature_adjustments:
            manual_adjustment = self.temperature_adjustments[agent_name]
            adjusted_temp = adjusted_temp * manual_adjustment
            
        # Ensure within valid range
        final_temp = max(0.0, min(1.0, adjusted_temp))
        
        # Record for analysis
        self._record_temperature_usage(agent_name, final_temp, query_type)
        
        return round(final_temp, 2)
        
    def _record_temperature_usage(self, agent_name: str, temperature: float, query_type: str):
        """Record temperature usage for optimization"""
        if agent_name not in self.performance_history:
            self.performance_history[agent_name] = []
            
        self.performance_history[agent_name].append({
            "timestamp": datetime.now().isoformat(),
            "temperature": temperature,
            "query_type": query_type
        })
        
        # Keep only recent history
        if len(self.performance_history[agent_name]) > 100:
            self.performance_history[agent_name] = self.performance_history[agent_name][-100:]
            
    def set_manual_adjustment(self, agent_name: str, multiplier: float):
        """Set manual temperature adjustment for an agent"""
        self.temperature_adjustments[agent_name] = max(0.5, min(1.5, multiplier))
        
    def get_temperature_analytics(self, agent_name: str) -> Dict[str, Any]:
        """Get temperature usage analytics"""
        history = self.performance_history.get(agent_name, [])
        
        if not history:
            return {"status": "no_data"}
            
        temps = [h["temperature"] for h in history]
        
        return {
            "average_temperature": sum(temps) / len(temps),
            "min_temperature": min(temps),
            "max_temperature": max(temps),
            "total_adjustments": len(history),
            "recent_trend": "increasing" if len(temps) > 1 and temps[-1] > temps[-2] else "stable"
        }


class DynamicPromptBuilder:
    """Build prompts dynamically based on context"""
    
    def __init__(self):
        self.prompt_templates = {}
        self.context_modifiers = {}
        self.success_patterns = {}
        
    def build_prompt(self, agent_name: str, agent_type: str, 
                    base_prompt: str, context: Dict[str, Any]) -> str:
        """Build enhanced prompt based on context"""
        
        enhanced_prompt = base_prompt
        
        # Add previous errors context
        if context.get("previous_errors"):
            error_context = self._build_error_context(context["previous_errors"])
            enhanced_prompt = f"{error_context}\n\n{enhanced_prompt}"
            
        # Add performance hints
        if context.get("performance_hints"):
            hints = "\n".join(f"- {hint}" for hint in context["performance_hints"])
            enhanced_prompt += f"\n\nPerformance hints:\n{hints}"
            
        # Add user expertise level adjustments
        if context.get("user_expertise"):
            expertise_modifier = self._get_expertise_modifier(context["user_expertise"])
            enhanced_prompt += f"\n\n{expertise_modifier}"
            
        # Add time constraints
        if context.get("time_constraint"):
            enhanced_prompt += f"\n\nTime constraint: Provide a {context['time_constraint']} response."
            
        # Add format preferences
        if context.get("format_preference"):
            enhanced_prompt += f"\n\nFormat preference: {context['format_preference']}"
            
        # Add successful pattern hints
        if agent_name in self.success_patterns:
            pattern_hint = self._get_pattern_hint(agent_name)
            if pattern_hint:
                enhanced_prompt += f"\n\n{pattern_hint}"
                
        return enhanced_prompt
        
    def _build_error_context(self, errors: List[str]) -> str:
        """Build context from previous errors"""
        if len(errors) == 1:
            return f"Note: A previous attempt encountered this issue: {errors[0]}. Please ensure your response addresses this."
        else:
            error_list = "\n".join(f"- {error}" for error in errors[-3:])  # Last 3 errors
            return f"Note: Previous attempts encountered these issues:\n{error_list}\nPlease ensure your response addresses these concerns."
            
    def _get_expertise_modifier(self, expertise: str) -> str:
        """Get prompt modifier based on user expertise"""
        modifiers = {
            "beginner": "Provide a clear, simple explanation avoiding technical jargon. Use analogies where helpful.",
            "intermediate": "Provide a balanced explanation with some technical details where appropriate.",
            "expert": "Provide technical details, implementation specifics, and advanced considerations.",
            "academic": "Provide rigorous analysis with citations and theoretical foundations where applicable."
        }
        
        return modifiers.get(expertise, "")
        
    def _get_pattern_hint(self, agent_name: str) -> Optional[str]:
        """Get hint based on successful patterns"""
        patterns = self.success_patterns.get(agent_name, [])
        
        if not patterns:
            return None
            
        # Use most successful pattern
        best_pattern = max(patterns, key=lambda p: p.get("success_count", 0))
        
        if best_pattern.get("hint"):
            return f"Hint: {best_pattern['hint']}"
            
        return None
        
    def register_success_pattern(self, agent_name: str, pattern: Dict[str, Any]):
        """Register a successful pattern for future use"""
        if agent_name not in self.success_patterns:
            self.success_patterns[agent_name] = []
            
        self.success_patterns[agent_name].append(pattern)
        
        # Keep only top 10 patterns
        if len(self.success_patterns[agent_name]) > 10:
            self.success_patterns[agent_name].sort(
                key=lambda p: p.get("success_count", 0), 
                reverse=True
            )
            self.success_patterns[agent_name] = self.success_patterns[agent_name][:10]


class TokenOptimizer:
    """Optimize token usage while maintaining quality"""
    
    @staticmethod
    def compress_prompt(prompt: str, target_reduction: float = 0.2) -> str:
        """Compress prompt while maintaining clarity"""
        
        original_length = len(prompt.split())
        
        # Step 1: Remove redundant whitespace
        compressed = " ".join(prompt.split())
        
        # Step 2: Apply common abbreviations
        abbreviations = {
            "artificial intelligence": "AI",
            "machine learning": "ML",
            "large language model": "LLM",
            "natural language processing": "NLP",
            "for example": "e.g.",
            "that is": "i.e.",
            "et cetera": "etc.",
            "versus": "vs.",
            "approximately": "~",
            "greater than": ">",
            "less than": "<",
            "equal to": "="
        }
        
        for full, abbr in abbreviations.items():
            compressed = compressed.replace(full, abbr)
            compressed = compressed.replace(full.title(), abbr)
            compressed = compressed.replace(full.upper(), abbr)
            
        # Step 3: Simplify verbose phrases
        simplifications = {
            "in order to": "to",
            "due to the fact that": "because",
            "in the event that": "if",
            "at this point in time": "now",
            "for the purpose of": "to",
            "with regard to": "about",
            "in accordance with": "per"
        }
        
        for verbose, simple in simplifications.items():
            compressed = compressed.replace(verbose, simple)
            
        # Step 4: Remove unnecessary articles in lists
        import re
        compressed = re.sub(r'\b(the|a|an)\s+(?=\w+[,;])', '', compressed)
        
        # Check if we achieved target reduction
        new_length = len(compressed.split())
        reduction = 1 - (new_length / original_length)
        
        logger.debug(f"Token optimization: {original_length} -> {new_length} tokens ({reduction:.1%} reduction)")
        
        return compressed
        
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimate token count (rough approximation)"""
        # Rough estimation: ~1.3 tokens per word for English
        word_count = len(text.split())
        
        # Adjust for code blocks and special content
        if "```" in text:
            # Code typically has more tokens per "word"
            return int(word_count * 1.5)
        else:
            return int(word_count * 1.3)
            
    @staticmethod
    def split_for_context_window(text: str, max_tokens: int = 3000, 
                                overlap: int = 200) -> List[str]:
        """Split text to fit in context window with overlap"""
        
        estimated_tokens = TokenOptimizer.estimate_tokens(text)
        
        if estimated_tokens <= max_tokens:
            return [text]
            
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for para in paragraphs:
            para_tokens = TokenOptimizer.estimate_tokens(para)
            
            if current_tokens + para_tokens > max_tokens - overlap:
                # Start new chunk
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                    # Keep last paragraph for overlap
                    current_chunk = [current_chunk[-1]] if len(current_chunk) > 0 else []
                    current_tokens = TokenOptimizer.estimate_tokens(current_chunk[0]) if current_chunk else 0
                    
            current_chunk.append(para)
            current_tokens += para_tokens
            
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            
        return chunks


class PromptCache:
    """Cache successful prompts for reuse"""
    
    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.access_counts = {}
        self.success_rates = {}
        self.max_size = max_size
        
    def _generate_key(self, agent_name: str, query: str) -> str:
        """Generate cache key"""
        content = f"{agent_name}:{query.lower().strip()}"
        return hashlib.md5(content.encode()).hexdigest()
        
    def get(self, agent_name: str, query: str, similarity_threshold: float = 0.9) -> Optional[str]:
        """Get cached prompt if available"""
        
        # Try exact match first
        key = self._generate_key(agent_name, query)
        
        if key in self.cache:
            self.access_counts[key] = self.access_counts.get(key, 0) + 1
            logger.debug(f"Cache hit for {agent_name}")
            return self.cache[key]["prompt"]
            
        # Try similar matches
        query_words = set(query.lower().split())
        best_match = None
        best_score = 0
        
        for cached_key, cached_data in self.cache.items():
            if cached_data["agent_name"] != agent_name:
                continue
                
            cached_words = set(cached_data["query"].lower().split())
            
            # Jaccard similarity
            intersection = len(query_words & cached_words)
            union = len(query_words | cached_words)
            similarity = intersection / union if union > 0 else 0
            
            if similarity >= similarity_threshold and similarity > best_score:
                best_score = similarity
                best_match = cached_key
                
        if best_match:
            self.access_counts[best_match] = self.access_counts.get(best_match, 0) + 1
            logger.debug(f"Similar cache hit for {agent_name} (similarity: {best_score:.2f})")
            return self.cache[best_match]["prompt"]
            
        return None
        
    def store(self, agent_name: str, query: str, prompt: str, 
             success: bool = True, response_quality: float = 1.0):
        """Store prompt in cache"""
        
        key = self._generate_key(agent_name, query)
        
        # Update success rate
        if key in self.success_rates:
            rate = self.success_rates[key]
            rate["count"] += 1
            rate["success_sum"] += 1 if success else 0
            rate["quality_sum"] += response_quality
        else:
            self.success_rates[key] = {
                "count": 1,
                "success_sum": 1 if success else 0,
                "quality_sum": response_quality
            }
            
        # Only cache successful prompts with good quality
        success_rate = self.success_rates[key]["success_sum"] / self.success_rates[key]["count"]
        avg_quality = self.success_rates[key]["quality_sum"] / self.success_rates[key]["count"]
        
        if success_rate >= 0.8 and avg_quality >= 0.8:
            self.cache[key] = {
                "agent_name": agent_name,
                "query": query,
                "prompt": prompt,
                "timestamp": datetime.now().isoformat(),
                "success_rate": success_rate,
                "quality": avg_quality
            }
            
            # Evict least accessed if over limit
            if len(self.cache) > self.max_size:
                self._evict_least_accessed()
                
            logger.debug(f"Cached prompt for {agent_name}")
            
    def _evict_least_accessed(self):
        """Remove least accessed cache entries"""
        
        # Sort by access count
        sorted_keys = sorted(
            self.cache.keys(), 
            key=lambda k: self.access_counts.get(k, 0)
        )
        
        # Remove bottom 10%
        remove_count = max(1, int(self.max_size * 0.1))
        
        for key in sorted_keys[:remove_count]:
            del self.cache[key]
            if key in self.access_counts:
                del self.access_counts[key]
            if key in self.success_rates:
                del self.success_rates[key]
                
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        
        total_accesses = sum(self.access_counts.values())
        
        return {
            "cache_size": len(self.cache),
            "total_accesses": total_accesses,
            "hit_rate": total_accesses / max(1, total_accesses + len(self.cache)),
            "most_accessed": sorted(
                self.access_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
        }