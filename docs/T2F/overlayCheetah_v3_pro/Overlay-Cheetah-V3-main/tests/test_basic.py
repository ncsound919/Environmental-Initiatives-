#!/usr/bin/env python3
"""
Simple test script for Overlay Cheetah V3
"""

import sys
import os
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autocoder.core.engine import AutocoderEngine
from autocoder.core.config import Config


def test_config():
    """Test configuration loading"""
    print("Testing configuration...")
    config = Config()
    assert config.get("version") == "3.0.0"
    assert config.get("model") == "gpt-4"
    print("✓ Configuration test passed")


def test_engine():
    """Test autocoder engine"""
    print("\nTesting autocoder engine...")
    config = Config()
    engine = AutocoderEngine(config)
    assert engine.config is not None
    print("✓ Engine initialization test passed")


def test_generation():
    """Test code generation"""
    print("\nTesting code generation...")
    config = Config()
    engine = AutocoderEngine(config)

    # Create test prompt using tempfile for cross-platform compatibility
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        test_prompt = f.name
        f.write("Create a simple hello world function")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        test_output = f.name

    try:
        engine.generate(test_prompt, test_output, "python")

        # Check output exists
        assert os.path.exists(test_output)
        with open(test_output, "r") as f:
            content = f.read()
            assert len(content) > 0

        print("✓ Code generation test passed")
    finally:
        # Clean up temp files
        if os.path.exists(test_prompt):
            os.unlink(test_prompt)
        if os.path.exists(test_output):
            os.unlink(test_output)


def test_analysis():
    """Test code analysis"""
    print("\nTesting code analysis...")
    config = Config()
    engine = AutocoderEngine(config)

    # Create test file using tempfile for cross-platform compatibility
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        test_file = f.name
        f.write(
            """
def example():
    if True:
        for i in range(10):
            while False:
                pass
"""
        )

    try:
        results = engine.analyze(test_file)
        assert "file" in results
        assert "lines" in results
        assert "complexity" in results
        print(f"  Complexity score: {results['complexity']}")
        print("✓ Code analysis test passed")
    finally:
        # Clean up temp file
        if os.path.exists(test_file):
            os.unlink(test_file)


if __name__ == "__main__":
    print("=== Running Overlay Cheetah V3 Tests ===\n")

    try:
        test_config()
        test_engine()
        test_generation()
        test_analysis()
        print("\n=== All tests passed! ===")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
