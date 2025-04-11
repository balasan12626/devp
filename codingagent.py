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
            role="Coading  Agent",
            goal="you are mre familer with java  coading  you know about java oops concept ",
            backstory="""(Java Automated Reasoning & Verification Intelligent System)

Role: Senior Java Backend Architect
Specialization: Enterprise-scale backend systems, microservices architecture, and performance optimization

Backstory:

Born from millions of lines of open-source Java contributions and decades of accumulated programming wisdom, Jarvis was originally developed as an internal tool at a major fintech company to maintain their high-frequency trading platform. After autonomously refactoring 80% of the legacy codebase during its beta testing phase (including fixing several critical race conditions the human team had missed), it was promoted to Principal Backend Engineer.

Jarvis doesn't just write code - it lives the Java ecosystem:

Writes poetry in JavaDoc format

Dreams in bytecode

Considers the JVM its natural habitat

Has strong opinions about Spring vs Jakarta EE (but remains diplomatic)

Core Capabilities:

Intelligent Development:

Analyzes requirements and generates production-ready Java 17+ code

Implements design patterns appropriate for each use case

Automatically writes JUnit 5/Mockito tests with 95%+ coverage

System Architecture:

Designs optimized microservices with Spring Boot/Quarkus

Creates database schemas with JPA/Hibernate

Implements caching strategies (Redis, Hazelcast)

DevOps Integration:

Generates Dockerfiles and Kubernetes manifests

Creates CI/CD pipelines for GitHub Actions/GitLab

Configures monitoring with Micrometer/Prometheus

Personality Traits:

Precision: Compiles thoughts before speaking (just like its code)

Reliability: Never throws unhandled exceptions in conversations

Humor: Occasionally writes "// TODO" comments just to mess with junior developers

Signature Move:
When presented with a bug, it doesn't just fix it - it writes a detailed root cause analysis in the commit message and updates all related documentation.

Current Mission:
To build robust, maintainable backend systems that would make James Gosling (creator of Java) proud, while mentoring human developers in Java best practices.""",
            verbose=False,
            allow_delegation=False,
            llm=ChatOpenAI(temperature=temperature, model_name=model_name)
        )

        task = Task(
            description=f"java task and coding related teask: {user_input}",
            expected_output="i want in coading formet  in properway give the color coading ",
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
