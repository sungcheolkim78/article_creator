# Enhanced Article Creator - Streamlit Application

A modern, user-friendly web interface for generating high-quality articles using AI with web search integration and multiple language support.

## Features

- 🚀 **Enhanced Article Generation**: Uses advanced AI models with ReACT reasoning
- 🌐 **Web Search Integration**: Real-time research using DuckDuckGo or Brave Search
- 🌍 **Multi-language Support**: Generate articles in English, Korean, Japanese, Chinese, Spanish, French, and German
- 📊 **Research-backed Content**: Articles are based on current web research and verified sources
- 💾 **Multiple Export Formats**: Save articles in translated, English, and research summary formats
- 🎨 **Modern UI**: Clean, responsive interface with real-time progress tracking

## Quick Start

### 1. Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root with your API keys:

```env
# Required for LLM models (choose one or more)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Optional for Brave Search (DuckDuckGo is free)
BRAVE_SEARCH_API_KEY=your_brave_search_api_key_here
```

### 3. Run the Streamlit Application

```bash
# From the project root
streamlit run src/app.py

# Or from the src directory
cd src
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Usage Guide

### 1. Configuration (Sidebar)

- **Article Topic**: Enter the topic you want to write about
- **Target Language**: Choose the language for the translated version
- **Generation Mode**: 
  - `enhanced`: Full research with ReACT agent (recommended)
  - `websearch`: Focused web search integration
- **ReACT Agent**: Enable/disable reasoning agent (enhanced mode only)
- **LLM Model**: Choose from OpenAI, Anthropic, or Gemini models
- **Search Tool**: DuckDuckGo (free) or Brave Search (requires API key)
- **Output Directory**: Where to save generated articles

### 2. Article Generation

1. Go to the "🚀 Article Generation" tab
2. Configure your settings in the sidebar
3. Click "Generate Article"
4. Wait for the generation process (may take 2-5 minutes)

### 3. Article Review

1. Go to the "📖 Article Review" tab
2. Switch between English and translated versions
3. Review the article content, sources, and research summary
4. Check generation metrics and parameters

### 4. Save & Export

1. Go to the "💾 Save & Export" tab
2. Click "Save Article to Files"
3. Download individual files or view saved locations

## Generated Files

Each article generation creates three files:

1. **Translated Version** (`topic-lang-timestamp.md`): Article in the target language
2. **English Version** (`topic-en-timestamp.md`): Original English article
3. **Research Summary** (`topic-research-timestamp.md`): Research findings and sources

## Supported Models

### LLM Models
- **OpenAI**: GPT-4o-mini, GPT-4o
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Haiku
- **Google**: Gemini 2.5 Flash

### Search Tools
- **DuckDuckGo**: Free, no API key required
- **Brave Search**: Requires API key, more comprehensive results

## Environment Check

The application automatically checks for required API keys and displays their status in the sidebar. Make sure you have at least one LLM API key configured.

## Troubleshooting

### Common Issues

1. **"API Key not found"**: Check your `.env` file and ensure API keys are correctly set
2. **"Search tool setup failed"**: For Brave Search, ensure you have a valid API key
3. **"Generation failed"**: Check your internet connection and API key validity
4. **"Module not found"**: Ensure all dependencies are installed with `uv sync`

### Performance Tips

- Use GPT-4o-mini for faster generation
- Enable ReACT agent for better research quality
- Use DuckDuckGo for free search functionality
- Generate articles during off-peak hours for better API response times

## Advanced Features

### ReACT Agent
The ReACT (Reasoning and Acting) agent enhances article quality by:
- Conducting systematic research
- Reasoning about information relevance
- Synthesizing findings into coherent content
- Fact-checking generated content

### Research Integration
- Real-time web search for current information
- Source verification and citation
- Multi-source synthesis
- Fact-checking and validation

## Contributing

Feel free to contribute to this project by:
- Reporting bugs
- Suggesting new features
- Improving the UI/UX
- Adding support for new languages or models

## License

This project is licensed under the MIT License - see the LICENSE file for details. 