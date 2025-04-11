import os
import streamlit as st
from crewai import Agent, Task, Crew, Process
from groq import Groq  # Assuming Grok provides a similar Python client
from bs4 import BeautifulSoup
import requests

# Set up the environment
os.environ["GROQ_API_KEY"] = "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"  # Replace with your actual key

# Initialize Grok client
client = Groq(api_key=os.environ["GROQ_API_KEY"])

# Streamlit UI setup
st.title("🌐 Web Scraping Agent with Grok Lama")
st.markdown("This agent scrapes websites and analyzes content using Grok Lama model")

# User inputs
url = st.text_input("Enter the URL to scrape:", "https://example.com")
query = st.text_input("What information are you looking for?", "Summarize the main content")
depth = st.selectbox("Scraping depth:", ["Surface (quick scan)", "Deep (full content)"])
submit_button = st.button("Start Scraping")

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
        allow_delegation=False,
        tools=[scrape_website]  # Custom tool we'll define
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

# Custom tool for web scraping
def scrape_website(url, depth="Surface (quick scan)"):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        if depth == "Deep (full content)":
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'iframe', 'noscript']):
                element.decompose()
            content = soup.get_text(separator='\n', strip=True)
        else:
            # Surface level - just get main content
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            if main_content:
                content = main_content.get_text(separator='\n', strip=True)
            else:
                content = soup.get_text(separator='\n', strip=True)
        
        return content[:15000]  # Limit to 15k characters to avoid context overflow
    except Exception as e:
        return f"Error scraping website: {str(e)}"

# Function to process with Grok Lama
def process_with_grok(prompt, content):
    try:
        response = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",  # Adjust based on actual Grok model name
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant that analyzes web content."},
                {"role": "user", "content": f"{prompt}\n\nHere's the content to analyze:\n{content}"}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error processing with Grok: {str(e)}"

# Main function to run the crew
def run_crew(url, query, depth):
    scraper, analyst = create_agents()
    
    # Create tasks
    scrape_task = Task(
        description=f"""Scrape the website at {url} with {depth} level scraping.
        Extract all relevant content while respecting robots.txt and ethical guidelines.""",
        agent=scraper,
        expected_output="Clean text content extracted from the website , i want in table formet  and point by point view."
    )
    
    analyze_task = Task(
        description=f"""Analyze the scraped content and {query}.
        Provide a comprehensive response that answers the user's query.""",
        agent=analyst,
        expected_output="A well-structured answer to the user's query based on the scraped content,i want in table formet ,point by point structure.",
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

if submit_button and url:
    with st.spinner("Scraping and analyzing the website..."):
        # First scrape the website
        scraped_content = scrape_website(url, depth)
        
        if scraped_content.startswith("Error"):
            st.error(scraped_content)
        else:
            st.success("Website scraped successfully!")
            with st.expander("View raw scraped content"):
                st.text(scraped_content[:5000] + ("..." if len(scraped_content) > 5000 else ""))
            
            # Now process with Grok
            st.info("Analyzing content with Grok Lama...")
            grok_response = process_with_grok(query, scraped_content)
            
            st.subheader("Analysis Results")
            st.markdown(grok_response)
            
            # Option to see the full process
            if st.checkbox("Show detailed process logs"):
                st.subheader("Detailed Process")
                st.text("This would show the CrewAI execution logs in a real implementation")