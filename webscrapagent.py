import os
import streamlit as st
from crewai import Agent, Task, Crew, Process
from groq import Groq
from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime

# Set up the environment
os.environ["GROQ_API_KEY"] = "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"

# Initialize Groq client
try:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
except Exception as e:
    st.error(f"Failed to initialize Groq client: {str(e)}")
    st.stop()

# Streamlit UI setup
st.set_page_config(page_title="Web Scraping Agent", page_icon="🌐")
st.title("🌐 Web Scraping Agent with Groq")
st.markdown("""
This agent scrapes websites and analyzes content using Groq's LLM models.
""")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    selected_model = st.selectbox(
        "Select Groq Model",
        ["mixtral-8x7b-32768", "llama2-70b-4096", "gemma-7b-it"],
        index=0
    )
    temperature = st.slider("Model Temperature", 0.0, 1.0, 0.7)
    max_tokens = st.slider("Max Tokens", 100, 4000, 2000)

# User inputs
col1, col2 = st.columns(2)
with col1:
    url = st.text_input("Enter the URL to scrape:", "https://example.com")
with col2:
    query = st.text_input("What information are you looking for?", "Summarize the main content")

depth = st.selectbox("Scraping depth:", ["Surface (quick scan)", "Deep (full content)"])
submit_button = st.button("Start Scraping & Analysis")

# Define agents
def create_agents():
    # Web Scraper Agent
    scraper = Agent(
        role='Senior Web Scraper',
        goal='Extract all relevant content from web pages efficiently and ethically',
        backstory="""You are an expert web scraper with years of experience in extracting 
        information from websites. You know how to identify main content, avoid boilerplate, 
        and handle different website structures.""",
        verbose=True,
        allow_delegation=False
    )
    
    # Research Analyst Agent
    analyst = Agent(
        role='Research Analyst',
        goal='Analyze and interpret scraped data to provide valuable insights',
        backstory="""You are a skilled analyst who can process raw data and extract 
        meaningful information. You specialize in summarizing, identifying key points, 
        and answering specific questions about content.""",
        verbose=True,
        allow_delegation=False
    )
    
    return scraper, analyst

# Enhanced web scraping function
def scrape_website(url, depth="Surface (quick scan)"):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        # Check URL scheme
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'iframe', 'noscript', 'svg']):
            element.decompose()
            
        if depth == "Deep (full content)":
            content = soup.get_text(separator='\n', strip=True)
        else:
            # Try to find main content areas
            selectors = ['main', 'article', 'div.content', 'div.main', 'div#content', 'div#main']
            main_content = None
            
            for selector in selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break
                    
            content = main_content.get_text(separator='\n', strip=True) if main_content else soup.get_text(separator='\n', strip=True)
        
        # Clean up content
        content = '\n'.join([line for line in content.split('\n') if line.strip()])
        return content[:15000]  # Limit to 15k characters
        
    except requests.exceptions.RequestException as e:
        return f"Request Error: {str(e)}"
    except Exception as e:
        return f"Scraping Error: {str(e)}"

# Enhanced Groq processing function
def process_with_grok(prompt, content, model=selected_model):
    try:
        system_prompt = """You are a helpful AI assistant that analyzes web content. 
        Provide responses in clear, structured formats with these preferences:
        - Use bullet points for lists
        - Use tables for comparative data
        - Highlight key points in bold
        - Include section headers
        - Format for readability"""
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{prompt}\n\nHere's the content to analyze:\n{content}"}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error processing with Groq: {str(e)}"

# Function to convert text to table format
def text_to_table(text):
    try:
        # This is a simple conversion - you might need to adjust based on your content
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if len(lines) < 2:
            return text  # Return original if not enough lines
        
        # Create a simple dataframe
        df = pd.DataFrame({
            "Point": range(1, len(lines)+1),
            "Content": lines
        })
        return df
    except:
        return text

# Main function to run the crew
def run_crew(url, query, depth):
    try:
        scraper, analyst = create_agents()
        
        # Create tasks
        scrape_task = Task(
            description=f"""Scrape the website at {url} with {depth} level scraping.
            Extract all relevant content while respecting robots.txt and ethical guidelines.
            Focus on extracting clean, readable text.""",
            agent=scraper,
            expected_output="Clean text content extracted from the website in a structured format."
        )
        
        analyze_task = Task(
            description=f"""Analyze the scraped content to: {query}.
            Provide a comprehensive response that answers the user's query.
            Use structured formats like tables and bullet points where appropriate.
            Include key insights and summaries.""",
            agent=analyst,
            expected_output="A well-structured answer to the user's query based on the scraped content.",
            context=[scrape_task]
        )
        
        # Form the crew
        crew = Crew(
            agents=[scraper, analyst],
            tasks=[scrape_task, analyze_task],
            process=Process.sequential,
            verbose=2
        )
        
        # Execute tasks
        result = crew.kickoff()
        return result
    except Exception as e:
        return f"CrewAI Error: {str(e)}"

if submit_button and url:
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Analysis Results", "Raw Content", "Process Details"])
    
    with st.spinner("Processing your request..."):
        start_time = datetime.now()
        
        # First scrape the website
        scraped_content = scrape_website(url, depth)
        
        with tab2:
            st.subheader("Raw Scraped Content")
            if scraped_content.startswith("Error"):
                st.error(scraped_content)
            else:
                st.text_area("Content", scraped_content, height=300)
                st.info(f"Content length: {len(scraped_content)} characters")
        
        if not scraped_content.startswith("Error"):
            # Process with Groq
            grok_response = process_with_grok(query, scraped_content)
            
            with tab1:
                st.subheader("Analysis Results")
                
                # Try to display as table if possible
                table_data = text_to_table(grok_response)
                if isinstance(table_data, pd.DataFrame):
                    st.dataframe(table_data, use_container_width=True)
                else:
                    st.markdown(grok_response)
                
                # Download buttons
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="Download as Markdown",
                        data=grok_response,
                        file_name="analysis_results.md",
                        mime="text/markdown"
                    )
                with col2:
                    if isinstance(table_data, pd.DataFrame):
                        st.download_button(
                            label="Download as CSV",
                            data=table_data.to_csv(index=False),
                            file_name="analysis_results.csv",
                            mime="text/csv"
                        )
            
            with tab3:
                st.subheader("Process Details")
                st.json({
                    "url": url,
                    "query": query,
                    "depth": depth,
                    "model": selected_model,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "processing_time": str(datetime.now() - start_time),
                    "content_length": len(scraped_content)
                })
                
                st.info("Note: In a full implementation, this would show detailed CrewAI execution logs")

# Add footer
st.markdown("---")
st.caption("Web Scraping Agent powered by Groq and CrewAI | Made with Streamlit")
