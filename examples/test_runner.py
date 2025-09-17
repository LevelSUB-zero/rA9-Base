#!/usr/bin/env python3
"""
RA9 Test Runner
Comprehensive testing suite for RA9 Cognitive Engine
"""

import subprocess
import sys
import json
from pathlib import Path

def run_pytest_tests():
    """Run pytest test suite"""
    print("🧪 Running Pytest Test Suite")
    print("=" * 40)
    
    try:
        # Run all tests
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", 
            "--tb=short"
        ], capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ All pytest tests passed!")
        else:
            print(f"❌ Some tests failed (exit code: {result.returncode})")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running pytest: {e}")
        return False

def run_quality_tests():
    """Run quality-specific tests"""
    print("\n🔍 Running Quality Tests")
    print("=" * 40)
    
    try:
        # Test quality guards
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_quality_guards.py", 
            "-v"
        ], capture_output=True, text=True)
        
        print("Quality Guards Test Results:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running quality tests: {e}")
        return False

def run_integration_tests():
    """Run integration tests"""
    print("\n🔗 Running Integration Tests")
    print("=" * 40)
    
    try:
        # Test integration quality
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_integration_quality.py", 
            "-v"
        ], capture_output=True, text=True)
        
        print("Integration Test Results:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running integration tests: {e}")
        return False

def run_brain_architecture_test():
    """Run complete brain architecture test"""
    print("\n🧠 Running Brain Architecture Test")
    print("=" * 40)
    
    try:
        from ra9.test_complete_brain_architecture import test_complete_brain_workflow
        
        # Test with a simple query
        test_query = "What is artificial intelligence?"
        print(f"Test Query: {test_query}")
        
        result = test_complete_brain_workflow(test_query)
        
        print("\nTest Results:")
        print(f"  - Success: {result.get('success', False)}")
        print(f"  - Final Answer: {result.get('final_answer', 'N/A')[:100]}...")
        
        if 'iteration_trace' in result:
            trace = result['iteration_trace']
            print(f"  - Iterations: {len(trace)}")
            
            for i, iteration in enumerate(trace):
                agents = len(iteration.get('agentOutputs', []))
                critiques = len(iteration.get('criticReports', []))
                coherence = iteration.get('coherence', {}).get('coherence_score', 'N/A')
                print(f"    Iteration {i+1}: {agents} agents, {critiques} critiques, coherence: {coherence}")
        
        if 'quarantine' in result:
            quarantine = result['quarantine']
            print(f"  - Quarantined Items: {len(quarantine)}")
            for item in quarantine:
                print(f"    - {item.get('reason', 'Unknown reason')}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Error running brain architecture test: {e}")
        return False

def run_import_tests():
    """Test all critical imports"""
    print("\n📦 Testing Critical Imports")
    print("=" * 40)
    
    imports_to_test = [
        "ra9",
        "ra9.core.engine",
        "ra9.core.schemas",
        "ra9.core.gating_manager",
        "ra9.core.agent_critique",
        "ra9.core.meta_coherence_engine",
        "ra9.core.neuromodulation_controller",
        "ra9.agents.logic_agent",
        "ra9.agents.emotion_agent",
        "ra9.agents.creative_agent",
        "ra9.agents.strategy_agent",
        "ra9.memory.memory_manager",
        "ra9.tools.search_agent"
    ]
    
    failed_imports = []
    
    for module in imports_to_test:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            failed_imports.append(module)
        except Exception as e:
            print(f"  ⚠️  {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ {len(failed_imports)} imports failed")
        return False
    else:
        print("\n✅ All critical imports successful")
        return True

def run_quality_summary():
    """Run quality summary and display metrics"""
    print("\n📊 Quality Summary")
    print("=" * 40)
    
    try:
        from ra9.core.cli_quality_summary import run_quality_summary
        
        metrics = run_quality_summary()
        
        print("Quality Metrics:")
        for key, value in metrics.items():
            print(f"  - {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error running quality summary: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print("🚀 RA9 Comprehensive Test Suite")
    print("=" * 60)
    print("Running all tests to verify RA9 installation and functionality")
    print("=" * 60)
    
    test_results = {}
    
    # Run all test categories
    test_results['imports'] = run_import_tests()
    test_results['pytest'] = run_pytest_tests()
    test_results['quality'] = run_quality_tests()
    test_results['integration'] = run_integration_tests()
    test_results['brain_architecture'] = run_brain_architecture_test()
    test_results['quality_summary'] = run_quality_summary()
    
    # Summary
    print("\n📋 Test Summary")
    print("=" * 40)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} test categories passed")
    
    if passed == total:
        print("🎉 All tests passed! RA9 is ready to use.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("Common issues:")
        print("  - Missing dependencies: Run 'pip install -e .'")
        print("  - Missing API key: Set GEMINI_API_KEY in .env file")
        print("  - Import errors: Check Python path and virtual environment")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
