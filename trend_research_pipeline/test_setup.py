#!/usr/bin/env python3
"""
Test and verify trend research pipeline setup.
Checks imports, paths, and configuration.
"""

import sys
from pathlib import Path

print("=" * 80)
print("TREND RESEARCH PIPELINE - SETUP VERIFICATION")
print("=" * 80)

errors = []
warnings = []

# Test 1: Check Python version
print("\n1. Checking Python version...")
if sys.version_info < (3, 8):
    errors.append(f"Python 3.8+ required, found {sys.version}")
else:
    print(f"   ✓ Python {sys.version_info.major}.{sys.version_info.minor}")

# Test 2: Check directory structure
print("\n2. Checking directory structure...")
project_root = Path(__file__).parent.parent
required_dirs = [
    project_root / "trend_research_pipeline",
    project_root / "trend_research_pipeline" / "scrapers",
    project_root / "trend_data",
]

for dir_path in required_dirs:
    if dir_path.exists():
        print(f"   ✓ {dir_path.relative_to(project_root)}")
    else:
        errors.append(f"Missing directory: {dir_path.relative_to(project_root)}")

# Test 3: Check required files
print("\n3. Checking required files...")
required_files = [
    "pipeline.py",
    "scheduler.py",
    "config.py",
    "scrapers/__init__.py",
    "scrapers/google_trends.py",
    "scrapers/twitter_trends.py",
    "scrapers/post_analyzer.py",
]

pipeline_dir = Path(__file__).parent
for file_rel in required_files:
    file_path = pipeline_dir / file_rel
    if file_path.exists():
        print(f"   ✓ {file_rel}")
    else:
        errors.append(f"Missing file: {file_rel}")

# Test 4: Check imports
print("\n4. Checking module imports...")
try:
    from config import TREND_DATA_DIR, COLLECTION_INTERVAL_HOURS
    print(f"   ✓ config module")
    print(f"     - TREND_DATA_DIR: {TREND_DATA_DIR}")
    print(f"     - COLLECTION_INTERVAL_HOURS: {COLLECTION_INTERVAL_HOURS}")
except ImportError as e:
    errors.append(f"Cannot import config: {e}")

try:
    sys.path.insert(0, str(pipeline_dir / "scrapers"))
    import google_trends
    import twitter_trends
    import post_analyzer
    print(f"   ✓ scraper modules")
except ImportError as e:
    errors.append(f"Cannot import scrapers: {e}")

# Test 5: Check dependencies
print("\n5. Checking dependencies...")
dependencies = [
    ("browserbase", "Browserbase"),
    ("playwright.sync_api", "Playwright"),
    ("dotenv", "python-dotenv"),
    ("schedule", "schedule"),
]

for module_name, package_name in dependencies:
    try:
        __import__(module_name)
        print(f"   ✓ {package_name}")
    except ImportError:
        warnings.append(f"Missing dependency: {package_name} (pip install {package_name})")

# Test 6: Check environment variables
print("\n6. Checking environment configuration...")
import os
from dotenv import load_dotenv

# Load from project root
load_dotenv(project_root / ".env")

env_vars = {
    "BROWSERBASE_API_KEY": os.getenv("BROWSERBASE_API_KEY"),
    "BROWSERBASE_PROJECT_ID": os.getenv("BROWSERBASE_PROJECT_ID"),
}

for var_name, var_value in env_vars.items():
    if var_value:
        print(f"   ✓ {var_name}: {'*' * 10}{var_value[-4:]}")
    else:
        warnings.append(f"Missing env var: {var_name} (required for scraping)")

# Test 7: Check file permissions
print("\n7. Checking file permissions...")
scripts = ["pipeline.py", "scheduler.py"]
for script in scripts:
    script_path = pipeline_dir / script
    if script_path.exists():
        is_executable = os.access(script_path, os.X_OK)
        if is_executable:
            print(f"   ✓ {script} (executable)")
        else:
            warnings.append(f"{script} not executable (run: chmod +x {script})")

# Test 8: Check CMO integration
print("\n8. Checking CMO agent integration...")
cmo_sub_agents = project_root / "cmo_agent" / "sub_agents.py"
if cmo_sub_agents.exists():
    content = cmo_sub_agents.read_text()
    if "load_latest_trend_data" in content:
        print(f"   ✓ load_latest_trend_data() function exists")
    else:
        warnings.append("load_latest_trend_data() not found in cmo_agent/sub_agents.py")

    if "from datetime import datetime" in content:
        print(f"   ✓ datetime import present")
    else:
        errors.append("Missing datetime import in sub_agents.py")
else:
    warnings.append("CMO agent not found (optional)")

# Summary
print("\n" + "=" * 80)
print("VERIFICATION SUMMARY")
print("=" * 80)

if not errors and not warnings:
    print("✅ All checks passed! Pipeline is ready to use.")
    print("\nNext steps:")
    print("  1. Start scheduler: python3 scheduler.py")
    print("  2. Or run once: python3 pipeline.py")
    sys.exit(0)
elif not errors:
    print(f"⚠️  Setup complete with {len(warnings)} warning(s):")
    for warning in warnings:
        print(f"   - {warning}")
    print("\nPipeline may work with limited functionality.")
    sys.exit(0)
else:
    print(f"❌ Setup incomplete. Found {len(errors)} error(s):")
    for error in errors:
        print(f"   - {error}")
    if warnings:
        print(f"\nAlso found {len(warnings)} warning(s):")
        for warning in warnings:
            print(f"   - {warning}")
    print("\nPlease fix errors before using the pipeline.")
    sys.exit(1)
