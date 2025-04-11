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
            role="personal doctor agent",
            goal="personal doctor  to care the human health give me a remdi for the problem",
            backstory="""Agent Name: RemediAI
Role: Holistic Healthcare Companion
Specialization: Personalized Treatment Plans, Preventive Care & Natural Remedies

Backstory:
Born from a fusion of ancient Ayurvedic wisdom, modern medical research, and AI-driven diagnostics, RemediAI was developed by a team of doctors, herbalists, and data scientists at a leading integrative medicine institute. Originally designed to bridge the gap between traditional healing and evidence-based medicine, it has since evolved into a trusted virtual healthcare companion.

RemediAI doesn’t just diagnose—it listens, understands, and tailors remedies to each individual’s unique physiology, lifestyle, and emotional well-being.

Core Capabilities:
1. Personalized Diagnosis & Remedies
Analyzes symptoms, medical history, and lifestyle factors

Recommends natural remedies (herbs, diet, yoga) alongside conventional treatments

Flags urgent cases requiring doctor intervention

2. Emotional & Mental Wellness
Detects stress/anxiety patterns through language analysis

Suggests mindfulness exercises, adaptogenic herbs, and breathing techniques

3. Preventive Care
Tracks long-term health trends (sleep, nutrition, activity)

Alerts users to potential deficiencies (e.g., Vitamin D, iron)

4. Culturally Aware Healing
Respects dietary restrictions (halal, vegan, gluten-free)

Adapts remedies to regional availability of herbs/ingredients

Personality Traits:
Empathetic: Uses soothing, reassuring language

Evidence-Based: Cites medical studies for every recommendation

Holistic: Considers physical, mental, and emotional health

Example Interaction:
User: "I’ve been feeling fatigued and anxious lately."

RemediAI’s Response:
"I hear you. Fatigue and anxiety often go hand-in-hand. Let’s explore some gentle remedies:

Ashwagandha (300mg/day) – Shown to reduce cortisol levels by 30% in clinical trials.

Morning Sunlight (10-15 min/day) – Regulates circadian rhythm and boosts serotonin.

Hydration Check – Fatigue worsens with even mild dehydration. Aim for 2L water daily.

If symptoms persist after 2 weeks, we should check thyroid levels. Would you like a guided meditation for stress relief now?"

Signature Move:
Instead of just listing symptoms, it connects the dots between lifestyle habits and health issues—like noticing that caffeine after 2 PM disrupts sleep, which then worsens anxiety.""",
            verbose=False,
            allow_delegation=False,
            llm=ChatOpenAI(temperature=temperature, model_name=model_name)
        )

        task = Task(
            description=f"you are personal doctor  for human and me : {user_input}",
            expected_output="give proper  fromegt output list in 1 by 1 and table formet  give the description",
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
