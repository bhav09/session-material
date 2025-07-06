import streamlit as st
import google.generativeai as genai
import os

API_KEY = os.getenv('GOOGLE_API_KEY')

# Configure the Gemini API
try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error(f"Failed to configure Gemini API. Please check your API key. Error: {e}")
    st.stop() # Stop the app if API key is invalid or missing

# Initialize the Gemini Pro model
# Using gemini-2.0-flash for faster responses, can be changed to gemini-1.5-pro for more detailed responses
model = genai.GenerativeModel('gemini-2.0-flash')

# --- Streamlit UI ---
st.set_page_config(page_title="Student Helper LLM", layout="wide")

st.title("📚 AI Teacher")
st.markdown("Your personal AI assistant for coding, learning, and data analysis!")

# Router in the sidebar
st.sidebar.header("Choose a Mode")
selected_mode = st.sidebar.radio(
    "Select what you need help with:",
    ("Code Debugger", "Topic Explainer", "Data Analysis Concepts")
)

st.sidebar.markdown("---")
st.sidebar.markdown("### How to Use:")
st.sidebar.markdown("- Select a mode from above.")
st.sidebar.markdown("- Enter your query in the text area.")
st.sidebar.markdown("- Click 'Get Explanation' to see the AI's response.")

# Main content area based on selected mode
user_input = ""
if selected_mode == "Code Debugger":
    st.header("🐛 Code Debugger")
    st.markdown("Paste your Python code below, and I'll help you find and fix errors.")
    user_input = st.text_area("Enter your Python code here:", height=300, placeholder="def my_function(x):\n  return x + y # This will cause an error!")
    prompt_prefix = (
        "You are an expert Python debugger for students. Analyze the following code, "
        "identify any errors (syntax, logical, runtime), explain why they occur, "
        "and provide the corrected code along with a clear explanation of the fix. "
        "Focus on simplicity for students. If the code is correct, explain what it does. "
        "\n\nCode:\n```python\n"
    )
    prompt_suffix = "\n```"
    full_prompt = f"{prompt_prefix}{user_input}{prompt_suffix}"

elif selected_mode == "Topic Explainer":
    st.header("💡 Topic Explainer")
    st.markdown("Enter any complex topic, and I'll explain it with simple examples.")
    user_input = st.text_input("Enter the topic you want to understand:", placeholder="Quantum Entanglement")
    prompt_prefix = (
        "You are an excellent educator. Explain the following complex topic in simple terms, "
        "using at least one easy-to-understand, real-world example. Focus on clarity and "
        "conciseness for students. \n\nTopic: "
    )
    full_prompt = f"{prompt_prefix}{user_input}"

elif selected_mode == "Data Analysis Concepts":
    st.header("📊 Data Analysis Concepts")
    st.markdown("Ask about any data analysis concept, and I'll explain it clearly.")
    user_input = st.text_input("Enter the data analysis concept:", placeholder="What is p-value?")
    prompt_prefix = (
        "You are a data science instructor. Explain the following data analysis concept "
        "clearly and concisely. Provide a brief, simple example if applicable. "
        "Focus on core principles for students. \n\nConcept: "
    )
    full_prompt = f"{prompt_prefix}{user_input}"

# Button to trigger the LLM
if st.button("Get Explanation", type="primary"):
    if user_input.strip() == "":
        st.warning("Please enter something to get an explanation.")
    else:
        with st.spinner("Thinking..."):
            try:
                # Generate content using the Gemini model
                response = model.generate_content(full_prompt)
                st.subheader("AI's Explanation:")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"An error occurred while generating the response: {e}")
                st.info("Please ensure your Gemini API key is correct and you have an active internet connection.")
