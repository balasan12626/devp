# tourist_chat_guide_app.py

import os
import streamlit as st
from langchain_community.chat_models import ChatOpenAI
from crewai import Agent, Task, Crew, Process
import traceback

# Streamlit setup
st.set_page_config(page_title="Tourist Chat Guide", page_icon="💬", layout="wide")

# API Key
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

with st.sidebar:
    st.title("🔧 Configuration")
    api_key = st.text_input("Enter your OpenAI API key:", type="password", key="api_key_input")
    if api_key:
        st.session_state.api_key = api_key
        os.environ["OPENAI_API_KEY"] = api_key
        st.success("API key set successfully!")

    st.markdown("---")
    model_name = st.selectbox("Choose AI Model:", ["gpt-4", "gpt-3.5-turbo"])
    temperature = st.slider("Creativity Level:", 0.1, 1.0, 0.7, 0.1)
    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.success("Chat cleared!")

# Title
st.title("🗺️ Chat with Your AI Tourist Guide in india")

# Chat function
def chat_with_guide(user_input, model_name, temperature):
    try:
        guide = Agent(
            role="Tour Guide in tamilnadu india",
            goal="Answer tourist questions and give travel tips in tamilnadu",
            backstory="""You're an expert travel advisor with detailed knowledge of 
            cities, landmarks, hidden gems, and local experiences.""",
            verbose=False,
            allow_delegation=False,
            llm=ChatOpenAI(temperature=temperature, model_name=model_name)
        )

        task = Task(
            description=f"Answer the following travel question: {user_input}",
            expected_output="A clear and helpful answer with travel tips",
            agent=guide
        )

        crew = Crew(
            agents=[guide],
            tasks=[task],
            verbose=False,
            process=Process.sequential
        )

        return crew.kickoff()

    except Exception as e:
        return f"❌ Error: {str(e)}\n\n{traceback.format_exc()}"

# Chat Input
user_input = st.chat_input("Ask about any destination or travel advice...")

# Chat History Display
for i, chat in enumerate(st.session_state.chat_history):
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# Handle User Input
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response = chat_with_guide(user_input, model_name, temperature)
        st.markdown(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
