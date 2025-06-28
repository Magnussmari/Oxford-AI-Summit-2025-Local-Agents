"""
Agents package for LocalMind Collective Demo
"""

from .base import PresentationAgent, CURRENT_DATE, OLLAMA_HOST
from .principal import PrincipalSynthesizer
from .domain import DomainSpecialist
from .web import WebHarvester
from .fact import FactValidator
from .quality import QualityAuditor
from .orchestrator import PresentationOrchestrator

__all__ = [
    'PresentationAgent', 
    'CURRENT_DATE', 
    'OLLAMA_HOST',
    'PrincipalSynthesizer',
    'DomainSpecialist',
    'WebHarvester',
    'FactValidator',
    'QualityAuditor',
    'PresentationOrchestrator'
]