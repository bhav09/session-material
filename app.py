import streamlit as st
import google.generativeai as genai
import json
import os

# with open('/content/credentials.json') as file:
#   data = json.load(file)
#   GOOGLE_API_KEY = data['GOOGLE_API_KEY']

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Configure Google Gemini API
try:
    genai.configure(api_key=GOOGLE_API_KEY)
except KeyError:
    st.error("Google API Key not found. Please set it in .streamlit/secrets.toml or as an environment variable.")
    st.stop()

# Set up the model
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 1024,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
    safety_settings=safety_settings
)

st.title("Healthcare Gemini Chatbot")
st.write("Ask me anything related to healthcare! (Please consult a medical professional for actual advice.)")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Hello! How can I help you with your healthcare questions today?"})

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask a healthcare question..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare chat history for the model, ensuring it's only healthcare-related
    # For a real application, you'd likely want more sophisticated prompt engineering
    # to enforce healthcare-only responses from Gemini.
    
    # We will prepend a system instruction to each user message to reinforce the healthcare context.
    # This is a basic way to guide the model. More advanced filtering or fine-tuning
    # would be needed for strict healthcare adherence.
    
    messages_for_gemini = []
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            messages_for_gemini.append({"role": msg["role"], "parts": [f"Healthcare related question: {msg['content']}"]})
        else: # assistant
            messages_for_gemini.append({"role": msg["role"], "parts": [msg['content']]})

    try:
        # Start a new chat session with the model and pass the history
        chat = model.start_chat(history=messages_for_gemini)
        response = chat.send_message(prompt, stream=True)

        # Display assistant response
        full_response = ""
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌") # Typing effect
            message_placeholder.markdown(full_response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.info("The chatbot is designed to answer healthcare-related questions. Please try rephrasing your question or ask something related to healthcare.")
        # Remove the last user message if the response failed
        st.session_state.messages = st.session_state.messages[:-1]
