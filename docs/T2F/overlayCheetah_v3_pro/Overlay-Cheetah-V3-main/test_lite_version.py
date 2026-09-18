#!/usr/bin/env python3
"""
Test script for OverlayCheetah V3 Lite
Tests non-GUI functionality
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))


def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import yaml

        print("✓ yaml import successful")
    except ImportError as e:
        print(f"✗ yaml import failed: {e}")
        return False

    try:
        import tkinter

        print("✓ tkinter import successful")
    except ImportError as e:
        print(f"✗ tkinter import failed: {e}")
        print("  Note: tkinter might not be available in headless environments")
        # Don't fail on tkinter in CI environments

    return True


def test_template_engine():
    """Test TemplateEngine class"""
    print("\nTesting TemplateEngine...")
    try:
        # Import without creating GUI
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "lite", "overlay_cheetah_v3_lite.py"
        )
        lite = importlib.util.module_from_spec(spec)

        # Mock tkinter if not available
        if "tkinter" not in sys.modules:
            sys.modules["tkinter"] = type(
                "tkinter",
                (),
                {
                    "Tk": lambda: None,
                    "StringVar": lambda **kw: None,
                    "IntVar": lambda **kw: None,
                    "DoubleVar": lambda **kw: None,
                    "BooleanVar": lambda **kw: None,
                },
            )
            sys.modules["tkinter.ttk"] = type(
                "ttk",
                (),
                {
                    "Progressbar": lambda **kw: None,
                },
            )
            sys.modules["tkinter.scrolledtext"] = type("scrolledtext", (), {})

        spec.loader.exec_module(lite)

        template = lite.TemplateEngine()
        inputs = {"name": "test_project", "features": 3}
        stack = {"frontend": "React", "backend": "FastAPI"}

        yaml_output = template.generate_yaml(inputs, stack)

        assert "test_project" in yaml_output
        assert "OverlayCheetah V3 Lite" in yaml_output
        print("✓ TemplateEngine works correctly")
        return True

    except Exception as e:
        print(f"✗ TemplateEngine test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_build_executor():
    """Test BuildExecutor class"""
    print("\nTesting BuildExecutor...")
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "lite", "overlay_cheetah_v3_lite.py"
        )
        lite = importlib.util.module_from_spec(spec)

        # Mock tkinter if not available
        if "tkinter" not in sys.modules:
            sys.modules["tkinter"] = type(
                "tkinter",
                (),
                {
                    "Tk": lambda: None,
                    "StringVar": lambda **kw: None,
                    "IntVar": lambda **kw: None,
                    "DoubleVar": lambda **kw: None,
                    "BooleanVar": lambda **kw: None,
                },
            )
            sys.modules["tkinter.ttk"] = type(
                "ttk",
                (),
                {
                    "Progressbar": lambda **kw: None,
                },
            )
            sys.modules["tkinter.scrolledtext"] = type("scrolledtext", (), {})

        spec.loader.exec_module(lite)

        builder = lite.BuildExecutor()
        test_yaml = "test: content"

        result_container = {}

        def callback(result):
            result_container["result"] = result

        builder.execute(test_yaml, callback)

        # The execute method calls the callback directly, no need to wait
        assert "result" in result_container
        assert result_container["result"]["success"]
        print("✓ BuildExecutor works correctly")

        # Clean up test file
        if os.path.exists("generated_template_lite.yaml"):
            os.remove("generated_template_lite.yaml")
            print("✓ Test file cleaned up")

        return True

    except Exception as e:
        print(f"✗ BuildExecutor test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_syntax():
    """Test Python syntax"""
    print("\nTesting Python syntax...")
    try:
        import py_compile

        py_compile.compile("overlay_cheetah_v3_lite.py", doraise=True)
        print("✓ Python syntax is valid")
        return True
    except Exception as e:
        print(f"✗ Syntax test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("OverlayCheetah V3 Lite - Test Suite")
    print("=" * 50)

    results = []

    results.append(("Imports", test_imports()))
    results.append(("Syntax", test_syntax()))
    results.append(("TemplateEngine", test_template_engine()))
    results.append(("BuildExecutor", test_build_executor()))

    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:20s} {status}")

    all_passed = all(result for _, result in results)

    print("=" * 50)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
