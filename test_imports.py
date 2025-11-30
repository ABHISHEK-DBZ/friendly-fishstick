"""Quick test to verify all imports work"""
import sys

print("Testing imports...")
print(f"Python version: {sys.version}")

try:
    from agent_framework import (
        Executor,
        WorkflowBuilder,
        ChatMessage,
        WorkflowContext,
        handler
    )
    print("✓ Agent Framework imports successful")
except ImportError as e:
    print(f"✗ Agent Framework import failed: {e}")
    sys.exit(1)

try:
    from openai import OpenAI
    print("✓ OpenAI imports successful")
except ImportError as e:
    print(f"✗ OpenAI import failed: {e}")
    sys.exit(1)

try:
    from PIL import Image
    print("✓ Pillow imports successful")
except ImportError as e:
    print(f"✗ Pillow import failed: {e}")
    sys.exit(1)

try:
    import requests
    from bs4 import BeautifulSoup
    print("✓ Web scraping imports successful")
except ImportError as e:
    print(f"✗ Web scraping imports failed: {e}")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.panel import Panel
    print("✓ Rich console imports successful")
except ImportError as e:
    print(f"✗ Rich imports failed: {e}")
    sys.exit(1)

try:
    import sqlite3
    print("✓ SQLite3 available")
except ImportError as e:
    print(f"✗ SQLite3 import failed: {e}")
    sys.exit(1)

print("\n🎉 All imports successful!")
print("\nNext steps:")
print("1. Add your GITHUB_TOKEN to .env file")
print("2. Get token from: https://github.com/settings/tokens")
print("3. Run: python cli.py")
