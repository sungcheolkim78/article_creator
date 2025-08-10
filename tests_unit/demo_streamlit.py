#!/usr/bin/env python3
"""
Demo script for the Enhanced Article Creator Streamlit Application.

This script demonstrates how to use the application with different configurations.
"""

import subprocess
import sys
from pathlib import Path


def print_demo_info():
    """Print demo information and instructions."""
    print("🎯 Enhanced Article Creator - Streamlit Demo")
    print("=" * 50)
    print()
    print("This demo will show you how to use the Streamlit application.")
    print()
    print("📋 Available Features:")
    print("  ✅ Enhanced article generation with ReACT agent")
    print("  ✅ Web search integration (DuckDuckGo/Brave)")
    print("  ✅ Multi-language support (EN, KO, JP, CN, ES, FR, DE)")
    print("  ✅ Research-backed content with sources")
    print("  ✅ Multiple export formats")
    print("  ✅ Modern, responsive UI")
    print()
    print("🚀 Quick Start Examples:")
    print()
    print("1. Basic Article Generation:")
    print("   - Topic: 'The impact of AI on jobs in 2024'")
    print("   - Language: Korean")
    print("   - Mode: Enhanced")
    print("   - Model: GPT-4o-mini")
    print("   - Search: DuckDuckGo (free)")
    print()
    print("2. Research-Intensive Article:")
    print("   - Topic: 'Latest developments in quantum computing'")
    print("   - Language: English")
    print("   - Mode: Enhanced with ReACT")
    print("   - Model: Claude 3.5 Sonnet")
    print("   - Search: Brave Search")
    print()
    print("3. Quick Web Search Article:")
    print("   - Topic: 'Trends in renewable energy 2024'")
    print("   - Language: Japanese")
    print("   - Mode: Websearch")
    print("   - Model: Gemini 2.5 Flash")
    print("   - Search: DuckDuckGo")
    print()


def check_environment():
    """Check if the environment is properly set up."""
    print("🔍 Environment Check:")
    print("-" * 30)

    # Check if app.py exists
    app_path = Path("src/app.py")
    if app_path.exists():
        print("✅ Streamlit app found")
    else:
        print("❌ Streamlit app not found")
        return False

    # Check if dependencies are installed
    try:
        import streamlit

        print(f"✅ Streamlit {streamlit.__version__} installed")
    except ImportError:
        print("❌ Streamlit not installed")
        return False

    # Check for API keys
    import os
    from dotenv import load_dotenv

    load_dotenv()

    api_keys = {
        "OPENAI_API_KEY": "OpenAI",
        "ANTHROPIC_API_KEY": "Anthropic",
        "GEMINI_API_KEY": "Gemini",
        "BRAVE_SEARCH_API_KEY": "Brave Search",
    }

    found_keys = []
    for key, name in api_keys.items():
        if os.getenv(key):
            print(f"✅ {name} API key found")
            found_keys.append(name)
        else:
            print(f"⚠️  {name} API key not found")

    if not found_keys:
        print("❌ No LLM API keys found! Please set at least one API key in .env file")
        return False

    print(f"✅ Environment ready! Found API keys for: {', '.join(found_keys)}")
    return True


def run_demo():
    """Run the Streamlit demo."""
    print("🚀 Starting Streamlit Application...")
    print("🌐 The application will open in your browser at http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the application")
    print("-" * 60)

    try:
        # Run the Streamlit application
        subprocess.run(
            [
                "uv",
                "run",
                "streamlit",
                "run",
                "src/app.py",
                "--server.port",
                "8501",
                "--server.address",
                "localhost",
            ]
        )
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user.")
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        return False

    return True


def main():
    """Main demo function."""
    print_demo_info()

    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        print("\n💡 Setup Instructions:")
        print("1. Install dependencies: uv sync")
        print("2. Create .env file with API keys")
        print("3. Run this demo again")
        sys.exit(1)

    print("\n✅ Environment is ready!")

    # Ask user if they want to continue
    response = input("\n🚀 Start the Streamlit application? (y/n): ").lower().strip()
    if response in ["y", "yes", ""]:
        run_demo()
    else:
        print("👋 Demo cancelled. You can run the application later with:")
        print("   python run_streamlit.py")
        print("   or")
        print("   uv run streamlit run src/app.py")


if __name__ == "__main__":
    main()
