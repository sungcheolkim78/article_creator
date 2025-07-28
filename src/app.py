"""
Streamlit application for the enhanced article creator

This application provides a user-friendly interface to generate articles using the enhanced article creator
and displays the output in different translation versions (English, Korean, and Research summary).
"""

import streamlit as st
import os
import sys
from pathlib import Path
import time
from datetime import datetime
import json
from typing import Dict, Any, Optional

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent))

from enhanced_article_creator import EnhancedDraftArticle, WebSearchArticleCreator
from bravesearch import OptimizedBraveSearch
from ddgsearch import OptimizedDDGSearch
from utils import llm_setup

# Page configuration
st.set_page_config(
    page_title="Enhanced Article Creator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .article-content {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #e9ecef;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        border: 1px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'article_generated' not in st.session_state:
        st.session_state.article_generated = False
    if 'current_article' not in st.session_state:
        st.session_state.current_article = None
    if 'generation_time' not in st.session_state:
        st.session_state.generation_time = None
    if 'generation_params' not in st.session_state:
        st.session_state.generation_params = None

def setup_search_tool(search_tool_name: str) -> Optional[Any]:
    """Setup and return the search tool based on user selection."""
    try:
        if search_tool_name == "brave":
            brave_api_key = os.getenv("BRAVE_SEARCH_API_KEY")
            if not brave_api_key:
                st.error("❌ BRAVE_SEARCH_API_KEY not found in environment variables.")
                st.info("Please set BRAVE_SEARCH_API_KEY for Brave Search functionality.")
                return None
            return OptimizedBraveSearch(api_key=brave_api_key, k=5, source="web")
        elif search_tool_name == "ddg":
            return OptimizedDDGSearch(k=5)
        else:
            st.error(f"❌ Invalid search tool: {search_tool_name}")
            return None
    except Exception as e:
        st.error(f"❌ Error setting up search tool: {str(e)}")
        return None

def generate_article(topic: str, language: str, mode: str, use_react: bool, 
                    llm_model: str, search_tool_name: str) -> Optional[Dict[str, Any]]:
    """Generate article using the enhanced article creator."""
    
    with st.spinner("🔄 Setting up LLM and search tools..."):
        try:
            # Setup LLM
            llm_setup(llm_model)
            
            # Setup search tool
            search_tool = setup_search_tool(search_tool_name)
            if not search_tool:
                return None
                
        except Exception as e:
            st.error(f"❌ Error during setup: {str(e)}")
            return None
    
    # Choose article generator based on mode
    if mode == "enhanced":
        with st.spinner("🔄 Initializing Enhanced Article Creator..."):
            article_generator = EnhancedDraftArticle(search_tool)
        
        with st.spinner("🔄 Generating enhanced article with research and ReACT integration..."):
            try:
                prediction = article_generator.forward(
                    topic=topic, language=language, use_react=use_react
                )
                return prediction
            except Exception as e:
                st.error(f"❌ Error generating enhanced article: {str(e)}")
                return None
                
    elif mode == "websearch":
        with st.spinner("🔄 Initializing Web Search Article Creator..."):
            article_generator = WebSearchArticleCreator(search_tool)
        
        with st.spinner("🔄 Generating article with web search integration..."):
            try:
                prediction = article_generator.forward(topic=topic, language=language)
                return prediction
            except Exception as e:
                st.error(f"❌ Error generating web search article: {str(e)}")
                return None
    else:
        st.error(f"❌ Invalid mode: {mode}")
        return None

def display_article_metrics(article_data: Dict[str, Any]):
    """Display metrics about the generated article."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Title Length", len(article_data.get('title', '')))
    
    with col2:
        sections_en = article_data.get('sections_en', [])
        total_en_words = sum(len(section.split()) for section in sections_en)
        st.metric("English Words", total_en_words)
    
    with col3:
        sections_other = article_data.get('sections_other', [])
        total_other_words = sum(len(section.split()) for section in sections_other)
        st.metric(f"{st.session_state.generation_params['language']} Words", total_other_words)
    
    with col4:
        st.metric("Sections", len(sections_en))

def display_article_content(article_data: Dict[str, Any], language: str):
    """Display the article content in a formatted way."""
    
    # Display title
    st.markdown(f"# {article_data.get('title', 'Untitled Article')}")
    
    # Display metrics
    display_article_metrics(article_data)
    
    # Display content based on language
    if language.lower() == "english":
        sections = article_data.get('sections_en', [])
        st.markdown("## Article Content (English)")
    else:
        sections = article_data.get('sections_other', [])
        st.markdown(f"## Article Content ({language})")
    
    # Display each section
    for i, section in enumerate(sections, 1):
        with st.expander(f"Section {i}", expanded=True):
            st.markdown(section)
    
    # Display sources if available
    if hasattr(article_data, 'key_sources') and article_data.key_sources:
        st.markdown("## Sources")
        for source in article_data.key_sources:
            st.markdown(f"- {source}")
    
    # Display research summary if available
    if hasattr(article_data, 'research_summary') and article_data.research_summary:
        with st.expander("Research Summary", expanded=False):
            st.markdown(article_data.research_summary)

def save_article_to_file(article_data: Dict[str, Any], topic: str, language: str, 
                        output_dir: str, generation_params: Dict[str, Any]):
    """Save the generated article to files."""
    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        topic_slug = topic.lower().replace(" ", "-").replace(",", "")
        lang_slug = language[:3].lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save translated version
        translated_file = output_path / f"{topic_slug}-{lang_slug}-{timestamp}.md"
        with open(translated_file, "w", encoding="utf-8") as f:
            f.write(f"# {article_data.get('title', 'Untitled Article')}\n\n")
            for section in article_data.get('sections_other', []):
                f.write(section)
                f.write("\n\n")
            
            # Add sources
            if hasattr(article_data, 'key_sources') and article_data.key_sources:
                f.write("## Sources\n\n")
                for source in article_data.key_sources:
                    f.write(f"- {source}\n")
        
        # Save English version
        english_file = output_path / f"{topic_slug}-en-{timestamp}.md"
        with open(english_file, "w", encoding="utf-8") as f:
            f.write(f"# {article_data.get('title', 'Untitled Article')}\n\n")
            for section in article_data.get('sections_en', []):
                f.write(section)
                f.write("\n\n")
            
            # Add sources
            if hasattr(article_data, 'key_sources') and article_data.key_sources:
                f.write("## Sources\n\n")
                for source in article_data.key_sources:
                    f.write(f"- {source}\n")
        
        # Save research summary if available
        if hasattr(article_data, 'research_summary') and article_data.research_summary:
            research_file = output_path / f"{topic_slug}-research-{timestamp}.md"
            with open(research_file, "w", encoding="utf-8") as f:
                f.write(f"# Research Summary: {article_data.get('title', 'Untitled Article')}\n\n")
                f.write(article_data.research_summary)
                f.write("\n\n")
                f.write("## Generation Parameters\n\n")
                f.write(f"- Topic: {generation_params['topic']}\n")
                f.write(f"- Language: {generation_params['language']}\n")
                f.write(f"- Mode: {generation_params['mode']}\n")
                f.write(f"- LLM Model: {generation_params['llm_model']}\n")
                f.write(f"- Search Tool: {generation_params['search_tool_name']}\n")
                f.write(f"- ReACT Agent: {'Enabled' if generation_params['use_react'] else 'Disabled'}\n")
                f.write(f"- Generated At: {generation_params['generation_time']}\n")
        
        return {
            'translated_file': str(translated_file),
            'english_file': str(english_file),
            'research_file': str(research_file) if hasattr(article_data, 'research_summary') else None
        }
        
    except Exception as e:
        st.error(f"❌ Error saving article to file: {str(e)}")
        return None

def main():
    """Main Streamlit application."""
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">📝 Enhanced Article Creator</h1>', unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # Topic input
        topic = st.text_area(
            "Article Topic",
            value="The impact of AI on jobs in 2024",
            height=100,
            help="Enter the topic for your article"
        )
        
        # Language selection
        language = st.selectbox(
            "Target Language",
            ["Korean", "English", "Japanese", "Chinese", "Spanish", "French", "German"],
            index=0,
            help="Select the language for the translated version"
        )
        
        # Generation mode
        mode = st.selectbox(
            "Generation Mode",
            ["enhanced", "websearch"],
            index=0,
            help="Enhanced: Full research with ReACT agent. Websearch: Focused web search integration."
        )
        
        # ReACT agent toggle (only for enhanced mode)
        use_react = True
        if mode == "enhanced":
            use_react = st.checkbox(
                "Use ReACT Agent",
                value=True,
                help="Enable ReACT reasoning agent for enhanced research"
            )
        
        # LLM model selection
        llm_model = st.selectbox(
            "LLM Model",
            [
                "openai/gpt-4o-mini",
                "openai/gpt-4o",
                "anthropic/claude-sonnet-4-20250514",
                "anthropic/claude-3-7-sonnet-20250219",
                "anthropic/claude-3-5-haiku-20241022",
                "gemini/gemini-2.5-flash-lite",
                "gemini/gemini-2.5-flash",
                "gemini/gemini-2.5-pro"
            ],
            index=0,
            help="Select the language model for article generation"
        )
        
        # Search tool selection
        search_tool_name = st.selectbox(
            "Search Tool",
            ["ddg", "brave"],
            index=0,
            help="DuckDuckGo (free) or Brave Search (requires API key)"
        )
        
        # Output directory
        output_dir = st.text_input(
            "Output Directory",
            value="data/articles",
            help="Directory to save generated articles"
        )
        
        # Environment info
        st.markdown("---")
        st.markdown("### 🔑 Environment Check")
        
        # Check API keys
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY")
        brave_key = os.getenv("BRAVE_SEARCH_API_KEY")
        
        if "openai" in llm_model:
            if openai_key:
                st.success("✅ OpenAI API Key found")
            else:
                st.error("❌ OpenAI API Key missing")
        elif "anthropic" in llm_model:
            if anthropic_key:
                st.success("✅ Anthropic API Key found")
            else:
                st.error("❌ Anthropic API Key missing")
        elif "gemini" in llm_model:
            if gemini_key:
                st.success("✅ Gemini API Key found")
            else:
                st.error("❌ Gemini API Key missing")
        
        if search_tool_name == "brave":
            if brave_key:
                st.success("✅ Brave Search API Key found")
            else:
                st.warning("⚠️ Brave Search API Key missing")
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["🚀 Article Generation", "📖 Article Review", "💾 Save & Export"])
    
    with tab1:
        st.markdown('<h2 class="sub-header">Article Generation</h2>', unsafe_allow_html=True)
        
        # Generation button
        if st.button("🚀 Generate Article", type="primary", use_container_width=True):
            if not topic.strip():
                st.error("❌ Please enter a topic for the article.")
            else:
                # Store generation parameters
                generation_params = {
                    'topic': topic,
                    'language': language,
                    'mode': mode,
                    'use_react': use_react,
                    'llm_model': llm_model,
                    'search_tool_name': search_tool_name,
                    'output_dir': output_dir,
                    'generation_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Generate article
                with st.spinner("🔄 Generating article... This may take a few minutes."):
                    article_data = generate_article(
                        topic=topic,
                        language=language,
                        mode=mode,
                        use_react=use_react,
                        llm_model=llm_model,
                        search_tool_name=search_tool_name
                    )
                
                if article_data:
                    # Store in session state
                    st.session_state.article_generated = True
                    st.session_state.current_article = article_data
                    st.session_state.generation_time = generation_params['generation_time']
                    st.session_state.generation_params = generation_params
                    
                    st.success("✅ Article generated successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to generate article. Please check your configuration and try again.")
        
        # Display generation info
        if not st.session_state.article_generated:
            st.markdown("""
            <div class="info-box">
                <h4>📋 How to use:</h4>
                <ol>
                    <li>Configure your settings in the sidebar</li>
                    <li>Enter your article topic</li>
                    <li>Click "Generate Article" to start</li>
                    <li>Review the generated article in the "Article Review" tab</li>
                    <li>Save your article in the "Save & Export" tab</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<h2 class="sub-header">Article Review</h2>', unsafe_allow_html=True)
        
        if st.session_state.article_generated and st.session_state.current_article:
            article_data = st.session_state.current_article
            
            # Language selector for review
            review_language = st.selectbox(
                "Select language to review:",
                ["English", st.session_state.generation_params['language']],
                index=0
            )
            
            # Display article content
            display_article_content(article_data, review_language)
            
            # Generation info
            with st.expander("📊 Generation Information", expanded=False):
                params = st.session_state.generation_params
                st.write(f"**Topic:** {params['topic']}")
                st.write(f"**Language:** {params['language']}")
                st.write(f"**Mode:** {params['mode']}")
                st.write(f"**LLM Model:** {params['llm_model']}")
                st.write(f"**Search Tool:** {params['search_tool_name']}")
                st.write(f"**ReACT Agent:** {'Enabled' if params['use_react'] else 'Disabled'}")
                st.write(f"**Generated At:** {params['generation_time']}")
        else:
            st.info("📝 No article generated yet. Please generate an article first in the 'Article Generation' tab.")
    
    with tab3:
        st.markdown('<h2 class="sub-header">Save & Export</h2>', unsafe_allow_html=True)
        
        if st.session_state.article_generated and st.session_state.current_article:
            st.markdown("""
            <div class="info-box">
                <h4>💾 Save Options:</h4>
                <p>Your article will be saved in multiple formats:</p>
                <ul>
                    <li><strong>Translated version:</strong> Article in the target language</li>
                    <li><strong>English version:</strong> Original English article</li>
                    <li><strong>Research summary:</strong> Research findings and sources</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("💾 Save Article to Files", type="primary", use_container_width=True):
                with st.spinner("💾 Saving article to files..."):
                    saved_files = save_article_to_file(
                        st.session_state.current_article,
                        st.session_state.generation_params['topic'],
                        st.session_state.generation_params['language'],
                        st.session_state.generation_params['output_dir'],
                        st.session_state.generation_params
                    )
                
                if saved_files:
                    st.success("✅ Article saved successfully!")
                    
                    # Display saved file information
                    st.markdown("### 📁 Saved Files:")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Translated Version:**")
                        st.code(saved_files['translated_file'])
                        
                        st.markdown(f"**English Version:**")
                        st.code(saved_files['english_file'])
                    
                    with col2:
                        if saved_files['research_file']:
                            st.markdown(f"**Research Summary:**")
                            st.code(saved_files['research_file'])
                        
                        # Download buttons
                        st.markdown("### 📥 Download Files:")
                        
                        # Read and provide download buttons for each file
                        for file_type, file_path in saved_files.items():
                            if file_path and Path(file_path).exists():
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    file_content = f.read()
                                
                                file_name = Path(file_path).name
                                st.download_button(
                                    label=f"Download {file_name}",
                                    data=file_content,
                                    file_name=file_name,
                                    mime="text/markdown"
                                )
        else:
            st.info("📝 No article generated yet. Please generate an article first in the 'Article Generation' tab.")

if __name__ == "__main__":
    main()