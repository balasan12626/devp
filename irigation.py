# import os
# import streamlit as st
# import requests
# from langchain_community.chat_models import ChatOpenAI
# from crewai import Agent, Task, Crew, Process
# import traceback

# # === Config ===
# st.set_page_config(page_title="🌾 Irrigation AI Planner", page_icon="💧", layout="wide")

# # === API KEYS ===
# OPENAI_API_KEY = "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"
# ACCUWEATHER_API_KEY = "LBAAZzifVvyPS5aaiUJ5qtGGYwwAG0sJ"

# os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# # === Streamlit Session State ===
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []

# # === Get Location Key from AccuWeather ===
# def get_location_key(city):
#     try:
#         url = f"http://dataservice.accuweather.com/locations/v1/cities/search"
#         params = {"apikey": ACCUWEATHER_API_KEY, "q": city}
#         response = requests.get(url, params=params)
#         data = response.json()
#         return data[0]["Key"] if data else None
#     except:
#         return None

# # === Get Weather Info ===
# def get_weather(city):
#     location_key = get_location_key(city)
#     if not location_key:
#         return f"Weather data not available for '{city}'"
    
#     url = f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}"
#     params = {"apikey": ACCUWEATHER_API_KEY}
#     response = requests.get(url, params=params)
#     data = response.json()
#     if data:
#         condition = data[0]["WeatherText"]
#         temp = data[0]["Temperature"]["Metric"]["Value"]
#         return f"{condition}, {temp}°C"
#     return "Unable to fetch weather info."

# # === Sidebar Configuration ===
# with st.sidebar:
#     st.title("⚙️ Configuration")
#     st.markdown("🔐 API Key is hardcoded for this demo.")
#     model_name = st.selectbox("Choose Model:", ["gpt-4", "gpt-3.5-turbo"])
#     temperature = st.slider("Creativity Level:", 0.1, 1.0, 0.7, 0.1)
#     if st.button("🗑️ Clear Chat"):
#         st.session_state.chat_history = []
#         st.success("Chat history cleared!")

# # === App Title ===
# st.title("🌾 AI-Powered Irrigation Planner - Tamil Nadu Farmers Guide")

# # === Chat Logic ===
# def chat_with_guide(user_input, model_name, temperature):
#     try:
#         # Extract city from input (last word)
#         city = user_input.strip().split()[-1]
#         weather = get_weather(city)

#         guide = Agent(
#             role="Smart Irrigation Planner Agent",
#             goal="Generate smart irrigation schedules using real weather, crop type, and soil condition.",
#             backstory=f"""
# The agent helps Tamil Nadu farmers manage irrigation based on crop type, soil, and weather. Current weather in {city}: {weather}
# Crops: paddy, sugarcane, groundnut, millets.
# Soil types: loamy, clay, sandy.
# """,
#             verbose=False,
#             allow_delegation=False,
#             llm=ChatOpenAI(temperature=temperature, model_name=model_name)
#         )

#         task = Task(
#             description=f"""
# Analyze this irrigation query based on the crop, soil type, and weather:
# '{user_input}'

# Return a weekly irrigation table in Markdown:
# | Day | Crop | Soil Type | Weather | Water Required (L) | Time |
# """,
#             expected_output="Markdown table for 7 days, with realistic values and times.",
#             agent=guide,
#         )

#         crew = Crew(
#             agents=[guide],
#             tasks=[task],
#             verbose=True,
#             process=Process.sequential,
#         )

#         return crew.kickoff()

#     except Exception as e:
#         return f"❌ Error: {str(e)}\n\n{traceback.format_exc()}"

# # === Chat Input ===
# user_input = st.chat_input("Enter your irrigation query... (e.g., 'groundnut in Salem')")

# # === Display Chat History ===
# for chat in st.session_state.chat_history:
#     with st.chat_message(chat["role"]):
#         st.markdown(chat["content"])

# # === On Submit ===
# if user_input:
#     st.session_state.chat_history.append({"role": "user", "content": user_input})
#     with st.chat_message("user"):
#         st.markdown(user_input)

#     with st.chat_message("assistant"):
#         response = chat_with_guide(user_input, model_name, temperature)
#         st.markdown(response)
#         st.session_state.chat_history.append({"role": "assistant", "content": response})





import os
import streamlit as st
from crewai import Agent, Task, Crew, Process
from langchain_community.chat_models import ChatOpenAI
from crewai_tools import SerperDevTool

# Set up your API keys
OPENAI_API_KEY = "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"
SERPER_API_KEY = "1079a39f788f0b67a649996db78f3f6e289cf77d"

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["SERPER_API_KEY"] = SERPER_API_KEY

# === Streamlit UI Config ===
st.set_page_config(page_title="🌾 Irrigation AI Planner - Tamil Nadu", page_icon="💧", layout="wide")

# === Streamlit Session State ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# === CrewAI with Serper Search ===
def run_with_serper_search(query, model_name="gpt-4", temperature=0.7):
    try:
        # Setup SerperDevTool for live search (specifically for Tamil Nadu, India)
        search_tool = SerperDevTool(
            country="in",  # Country code for India
            locale="en",   # English locale
            location="Tamil Nadu, India",  # Search based on Tamil Nadu, India
            n_results=2    # Number of search results to return
        )

        # Create an agent that uses the Serper search tool
        agent = Agent(
            role="Irrigation Assistant",
            goal="An intelligent assistant that automates irrigation scheduling by analyzing environmental data and predicting optimal watering times.",
            backstory=f"""Provide smart irrigation schedules based on live data (weather, crops, soil,wethere climite ) . give me inn properf romet and one by one it posible displ;ay in table formet clearly   you canm take dessction making  asking yes or no you can take the desction making
            ✅ Prompt Example (like what you want):
"Create a backstory of a smart irrigation plant located in a village. Use separate weather data for each month. The story should describe how the irrigation system reacts to changing weather conditions like hot, cold, rainy, cloudy. Use your own decisions. At the end, give a table format with average monthly weather."

🧠 Backstory (AI-generated)
In the quiet village of Thendralpuram, nestled between dry plains and green hills, farmers once struggled to grow crops due to unpredictable weather. Some years brought harsh sun and cracked earth. Other times, rains flooded the fields.

In 2023, a group of young engineers installed a Smart Irrigation Plant in the heart of the village. It was connected to weather sensors and powered by AI. The system was trained to understand seasonal patterns and decide when to irrigate crops.

🌞 Summer Months (March to May)
In March, the temperature began to rise. April brought heat waves touching 38°C. The system reduced daytime watering and switched to early mornings and late evenings to prevent water evaporation.

🌧️ Monsoon Months (June to September)
By June, clouds gathered. The system detected increased humidity and paused watering during heavy rains. In July and August, rainfall peaked. The system diverted excess water to underground tanks to reuse during dry spells.

🍂 Post-Monsoon (October, November)
October was cloudy but dry. November brought light showers. The irrigation plant adjusted to shorter watering intervals. AI predicted fungal risks in crops due to moisture, so it warned farmers to switch fertilizers.

❄️ Winter (December to February)
Cold winds swept through December. Watering was scheduled at mid-day when temperatures were warmest (around 21°C). The system prevented frost damage by keeping soil temperature stable using covered drip lines.

By the end of the year, crop yield increased by 40%, and water usage dropped by 55%.

📊 Average Monthly Weather Table
Month	Avg Temp (°C)	Weather Condition
January	19	Cold & Dry
February	22	Cold & Sunny
March	29	Warm & Dry
April	35	Hot
May	38	Very Hot
June	32	Cloudy & Rainy
July	28	Rainy
August	27	Rainy & Humid
September	29	Rainy & Cloudy
October	30	Cloudy
November	26	Cool & Cloudy
December	21	Cold
            
            
            """,
             tools=[search_tool],
            #  memoryview="long-term",
            verbose=True,
            allow_delegation=False,
            llm=ChatOpenAI(temperature=temperature, model_name=model_name)
        )

        # Task that defines the query and expected output
        task = Task(
            description=f"Search and respond to the following wethere and quary curent wethere  give expline very breafly query: {query}",
            expected_output="give me a data of crops and seasaon  how plant the water  in table formet  point by point  way ",
            agent=agent
        )

        # Run CrewAI process
        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,  # Sequential process execution
            verbose=True
        )

        return crew.kickoff()

    except Exception as e:
        return f"❌ Error: {str(e)}"

# === Streamlit UI ===
st.title("🌾 AI-Powered Irrigation Planner - Tamil Nadu")

# Chat Input UI
user_input = st.text_input("Enter your irrigation query (e.g., 'weather forecast for groundnut in Tamil Nadu this week')")

# Display Chat History
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# On Submit
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response = run_with_serper_search(user_input)
        st.markdown(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
