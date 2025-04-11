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
            role="TIrrigation Planner Agent",
            goal="An intelligent assistant that automates irrigation scheduling by analyzing environmental data and predicting optimal watering times.",
            backstory="""Project Location: Tamil Nadu, India

Agriculture is the backbone of Tamil Nadu's rural economy, with lakhs of farmers depending on it for their livelihood. However, in recent years, the sector has faced increasing challenges due to erratic monsoons, rising temperatures, and acute water shortages. In particular, farmers in regions like Delta districts, Salem, and Dharmapuri often struggle to decide when and how much to irrigate—leading to either over-irrigation, which wastes water and harms the soil, or under-irrigation, which affects crop yield.

Recognizing the urgent need for smart water management, a collaborative team of agronomists, environmental scientists, and AI engineers launched the Irrigation Scheduling Project in Tamil Nadu. The goal: to develop a technology-driven solution that empowers farmers to irrigate efficiently using data and AI.

This vision gave birth to the Irrigation Planner Agent—an AI-powered assistant that leverages:

Soil moisture sensors embedded in the fields,

Weather forecast data specific to Tamil Nadu (including rainfall predictions),

And historical crop data for regional varieties like paddy, groundnut, sugarcane, and millets.

The agent is trained to analyze this data and generate an optimal weekly irrigation schedule that tells farmers:

Which days to irrigate,

How much water to use, and

What time of day irrigation would be most effective.

By doing so, the system helps conserve water, improve yields, and reduce labor and guesswork for farmers. It is especially beneficial for small and marginal farmers who lack access to expensive automated irrigation systems.

With Tamil Nadu facing increasing climate variability, the Irrigation Planner Agent is not just a tool—it's a step toward sustainable agriculture, climate resilience, and digital empowerment of Indian farmers..""",
            verbose=False,
            allow_delegation=False,
            llm=ChatOpenAI(temperature=temperature, model_name=model_name)
        )

        task = Task(
            description=f"Generate daily Irrigation Schedule: {user_input}",
            expected_output="A clear  give irrigation schedule i  want in table formet data  in formeted way ",
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
