#!/usr/bin/env python3
"""
Quick test script for enhanced orchestrator - just verifies initialization
"""

import asyncio
import sys
import os
from pathlib import Path
from loguru import logger

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.orchestrator_enhanced import ProductionOrchestrator


async def test_initialization():
    """Test that all enhanced components initialize correctly"""
    
    logger.info("Testing Enhanced Orchestrator Initialization...")
    
    try:
        # Create orchestrator
        orchestrator = ProductionOrchestrator(use_enhanced=True)
        print("✅ ProductionOrchestrator created")
        
        # Test all components exist
        assert hasattr(orchestrator, 'memory_system'), "Missing memory_system"
        print("✅ Memory system initialized")
        
        assert hasattr(orchestrator, 'communication'), "Missing communication"
        print("✅ Communication protocol initialized")
        
        assert hasattr(orchestrator, 'coordinator'), "Missing coordinator"
        print("✅ Agent coordinator initialized")
        
        assert hasattr(orchestrator, 'health_monitor'), "Missing health_monitor"
        print("✅ Health monitor initialized")
        
        assert hasattr(orchestrator, 'prompt_cache'), "Missing prompt_cache"
        print("✅ Prompt cache initialized")
        
        assert hasattr(orchestrator, 'prompt_builder'), "Missing prompt_builder"
        print("✅ Dynamic prompt builder initialized")
        
        # Test wrapped agents
        assert hasattr(orchestrator.principal, 'agent'), "Principal not wrapped"
        print("✅ Principal agent wrapped with resilience")
        
        assert hasattr(orchestrator.domain_specialist, 'agent'), "Domain specialist not wrapped"
        print("✅ Domain specialist wrapped with resilience")
        
        # Test system health
        health = orchestrator.get_system_health()
        assert 'agents' in health, "Missing agents in health report"
        assert 'memory_system' in health, "Missing memory_system in health report"
        assert 'communication' in health, "Missing communication in health report"
        print("✅ System health reporting working")
        
        # Test memory system database
        assert os.path.exists(orchestrator.memory_system.db_path), "Memory database not created"
        print(f"✅ Memory database created at: {orchestrator.memory_system.db_path}")
        
        # Test communication context
        orchestrator.communication.set_global_context("test_key", "test_value")
        context = orchestrator.communication.get_global_context("test_key")
        assert context == "test_value", "Communication context not working"
        print("✅ Communication context storage working")
        
        # Test cache stats
        stats = orchestrator.prompt_cache.get_cache_stats()
        assert 'cache_size' in stats, "Cache stats not working"
        print("✅ Cache statistics working")
        
        return True
        
    except Exception as e:
        logger.error(f"Initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_standard_mode():
    """Test that standard mode still works"""
    
    logger.info("\nTesting Standard Mode...")
    
    try:
        from agents.orchestrator import PresentationOrchestrator
        
        orchestrator = PresentationOrchestrator()
        print("✅ Standard orchestrator created")
        
        # Verify it doesn't have enhanced features
        assert not hasattr(orchestrator, 'memory_system'), "Standard mode has memory_system"
        assert not hasattr(orchestrator, 'communication'), "Standard mode has communication"
        print("✅ Standard mode correctly excludes enhanced features")
        
        return True
        
    except Exception as e:
        logger.error(f"Standard mode test failed: {e}")
        return False


async def main():
    """Run all quick tests"""
    
    print("="*60)
    print("LocalMind Enhanced Orchestrator Quick Test")
    print("="*60)
    
    # Test 1: Enhanced initialization
    test1_passed = await test_initialization()
    
    # Test 2: Standard mode
    test2_passed = await test_standard_mode()
    
    print("\n" + "="*60)
    print("Quick Test Results:")
    print(f"  Enhanced Initialization: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"  Standard Mode: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print("="*60)
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Enhanced features are ready to use.")
        print("\nTo test with actual queries, run the demo server:")
        print("  ./launch.sh")
    else:
        print("\n❌ Some tests failed. Check the errors above.")


if __name__ == "__main__":
    asyncio.run(main())