#!/usr/bin/env python3
"""
Test branding assets integration
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_branding_assets():
    """Test that branding assets exist and are accessible"""
    print("Testing branding assets...")

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Check for branding directory
    branding_dir = os.path.join(repo_root, "assets", "branding")
    assert os.path.exists(branding_dir), f"Branding directory not found: {branding_dir}"
    print(f"  ✓ Branding directory exists: {branding_dir}")

    # Check for logo
    logo_path = os.path.join(branding_dir, "overlay-cheetah-logo.svg")
    assert os.path.exists(logo_path), f"Logo not found: {logo_path}"
    assert os.path.getsize(logo_path) > 0, "Logo file is empty"
    print(f"  ✓ Logo exists: {logo_path} ({os.path.getsize(logo_path)} bytes)")

    # Check for brand image
    brand_path = os.path.join(branding_dir, "overlay365-brand.svg")
    assert os.path.exists(brand_path), f"Brand image not found: {brand_path}"
    assert os.path.getsize(brand_path) > 0, "Brand image file is empty"
    print(f"  ✓ Brand image exists: {brand_path} ({os.path.getsize(brand_path)} bytes)")

    # Check for README in branding directory
    readme_path = os.path.join(branding_dir, "README.md")
    assert os.path.exists(readme_path), f"Branding README not found: {readme_path}"
    print(f"  ✓ Branding README exists: {readme_path}")

    # Verify SVG files are valid (basic check)
    with open(logo_path, "r") as f:
        logo_content = f.read()
        assert "<svg" in logo_content, "Logo doesn't appear to be a valid SVG"
        assert "</svg>" in logo_content, "Logo SVG not properly closed"
    print("  ✓ Logo is valid SVG")

    with open(brand_path, "r") as f:
        brand_content = f.read()
        assert "<svg" in brand_content, "Brand image doesn't appear to be a valid SVG"
        assert "</svg>" in brand_content, "Brand image SVG not properly closed"
    print("  ✓ Brand image is valid SVG")

    print("✓ All branding assets tests passed")


def test_readme_integration():
    """Test that README files reference the branding assets"""
    print("\nTesting README integration...")

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Check main README
    main_readme = os.path.join(repo_root, "README.md")
    with open(main_readme, "r") as f:
        content = f.read()
        assert (
            "assets/branding/overlay-cheetah-logo.svg" in content
        ), "Main README doesn't reference logo"
        assert (
            "assets/branding/overlay365-brand.svg" in content
        ), "Main README doesn't reference brand image"
        assert "Overlay365" in content, "Main README doesn't mention Overlay365"
    print("  ✓ Main README.md has branding references")

    # Check docs README
    docs_readme = os.path.join(repo_root, "docs", "README.md")
    with open(docs_readme, "r") as f:
        content = f.read()
        assert (
            "../assets/branding/overlay-cheetah-logo.svg" in content
        ), "Docs README doesn't reference logo"
        assert (
            "../assets/branding/overlay365-brand.svg" in content
        ), "Docs README doesn't reference brand image"
    print("  ✓ docs/README.md has branding references")

    print("✓ All README integration tests passed")


def test_lite_version_integration():
    """Test that overlay_cheetah_v3_lite.py has branding guidance"""
    print("\nTesting Lite version integration...")

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    lite_file = os.path.join(repo_root, "overlay_cheetah_v3_lite.py")

    with open(lite_file, "r") as f:
        content = f.read()
        assert (
            "BRANDING INTEGRATION GUIDE" in content
        ), "Lite version doesn't have branding integration guide"
        assert (
            "assets/branding/overlay-cheetah-logo.svg" in content
        ), "Lite version doesn't reference logo path"
        assert (
            "assets/branding/overlay365-brand.svg" in content
        ), "Lite version doesn't reference brand image path"
        assert (
            "Splash Screen Integration" in content
        ), "Lite version doesn't have splash screen guidance"
        assert (
            "About Dialog Integration" in content
        ), "Lite version doesn't have about dialog guidance"
    print("  ✓ overlay_cheetah_v3_lite.py has branding integration comments")

    print("✓ All Lite version integration tests passed")


def test_manifest_and_setup():
    """Test that MANIFEST.in and setup.py include branding assets"""
    print("\nTesting packaging configuration...")

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Check MANIFEST.in
    manifest_file = os.path.join(repo_root, "MANIFEST.in")
    assert os.path.exists(manifest_file), "MANIFEST.in not found"
    with open(manifest_file, "r") as f:
        content = f.read()
        assert (
            "assets/branding" in content
        ), "MANIFEST.in doesn't include assets/branding"
    print("  ✓ MANIFEST.in includes branding assets")

    # Check setup.py
    setup_file = os.path.join(repo_root, "setup.py")
    with open(setup_file, "r") as f:
        content = f.read()
        assert (
            "include_package_data=True" in content
        ), "setup.py doesn't have include_package_data=True"
    print("  ✓ setup.py configured to include package data via MANIFEST.in")

    print("✓ All packaging configuration tests passed")


if __name__ == "__main__":
    print("=== Running Branding Integration Tests ===\n")

    try:
        test_branding_assets()
        test_readme_integration()
        test_lite_version_integration()
        test_manifest_and_setup()
        print("\n=== All branding integration tests passed! ===")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ Test failed: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
