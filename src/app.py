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

from utils.utils import (
    generate_article, 
    calculate_article_metrics, 
    save_article_to_file, 
    check_environment,
    get_available_llm_models,
    get_available_languages,
    get_available_search_tools,
    get_available_modes
)

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

def display_article_metrics(article_data: Dict[str, Any]):
    """Display metrics about the generated article."""
    metrics = calculate_article_metrics(article_data)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Title Length", metrics['title_length'])
    
    with col2:
        st.metric("English Words", metrics['total_en_words'])
    
    with col3:
        st.metric(f"{st.session_state.generation_params['language']} Words", metrics['total_other_words'])
    
    with col4:
        st.metric("Sections", metrics['sections_count'])

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

def check_environment_streamlit(llm_model: str, search_tool_name: str):
    """Check if required environment variables are set and display results in Streamlit."""
    env_check = check_environment(llm_model, search_tool_name)
    
    if "openai" in llm_model:
        if env_check['llm_key_found']:
            st.success("✅ OpenAI API Key found")
        else:
            st.error("❌ OpenAI API Key missing")
    elif "anthropic" in llm_model:
        if env_check['llm_key_found']:
            st.success("✅ Anthropic API Key found")
        else:
            st.error("❌ Anthropic API Key missing")
    elif "gemini" in llm_model:
        if env_check['llm_key_found']:
            st.success("✅ Gemini API Key found")
        else:
            st.error("❌ Gemini API Key missing")
    
    if search_tool_name == "brave":
        if env_check['search_key_found']:
            st.success("✅ Brave Search API Key found")
        else:
            st.warning("⚠️ Brave Search API Key missing")

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
            get_available_languages(),
            index=0,
            help="Select the language for the translated version"
        )
        
        # Generation mode
        mode = st.selectbox(
            "Generation Mode",
            get_available_modes(),
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
            get_available_llm_models(),
            index=0,
            help="Select the language model for article generation"
        )
        
        # Search tool selection
        search_tool_name = st.selectbox(
            "Search Tool",
            get_available_search_tools(),
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
        check_environment_streamlit(llm_model, search_tool_name)
    
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