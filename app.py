import streamlit as st
import subprocess
import tempfile
import os
import google.generativeai as genai

# Page configuration must be first Streamlit command
st.set_page_config(page_title="AI Tutor Academy", layout="wide")

# Set your Google API key from sidebar input (for Gemini)
api_key_input = st.sidebar.text_input("Enter your Google API Key for Gemini:", type="password")
if api_key_input:
    genai.configure(api_key=api_key_input)
else:
    st.sidebar.warning("Please enter your API Key to use AI Tutor.")
    st.stop()

# Initialize session state for AI chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"author": "system", "content": "You are an AI tutor that helps students learn Python. Provide clear, concise, and helpful explanations."}
    ]

# Sample question in English
sample_question = """
Write a Python function that takes a list of integers and returns the count of positive elements. Example: input [1, -2, 3, 4, -5] returns 3.
"""

# Layout with two columns: left for question & terminal, right for AI tutor
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Python Question and Terminal")
    st.subheader("Question:")
    st.code(sample_question, language="python")

    # Code editor
    code = st.text_area("Write your Python code here:", height=200, value="""def count_positive(numbers):
    # Start writing your code here
    pass

# Example usage:
# print(count_positive([1, -2, 3, 4, -5]))  # Output: 3
""")

    # Run button
    if st.button("Run Code"):
        # Save code to a temporary file and run it
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp_file:
            tmp_file.write(code.encode('utf-8'))
            tmp_file_path = tmp_file.name
        try:
            # Execute the code and capture output
            result = subprocess.run(
                ["python", tmp_file_path],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                st.subheader("Output:")
                st.code(result.stdout)
            else:
                st.subheader("Error:")
                st.code(result.stderr)
        except subprocess.TimeoutExpired:
            st.error("Code execution exceeded the time limit.")
        finally:
            # Cleanup temporary file
            os.remove(tmp_file_path)

with col2:
    st.header("AI Tutor")
    
    # Placeholder for chat history
    chat_container = st.empty()
    
    # Function to display chat history
    def display_chat():
        with chat_container.container():
            for msg in st.session_state.messages:
                if msg.get("author") == "user":
                    st.markdown(f"**You:** {msg['content']}")
                elif msg.get("author") in ["assistant", "system"]:
                    prefix = "Tutor" if msg.get("author") != "system" else "Tutor"
                    st.markdown(f"**{prefix}:** {msg['content']}")

    # Display initial chat history
    display_chat()

    # User input for AI tutor
    user_input = st.text_input("Ask the Tutor about the question or your code:")
    if st.button("Send", key="send_ai") and user_input:
        # Append user message
        st.session_state.messages.append({"author": "user", "content": user_input})
        
        # Call Google Generative AI API
        try:
            model = genai.GenerativeModel('models/gemini-flash-2.0')
            formatted_messages = [
                {"role": m["author"], "parts": [{"text": m["content"]}]}
                for m in st.session_state.messages
            ]
            response = model.generate_content(formatted_messages)
            assistant_message = response.text
            st.session_state.messages.append({"author": "assistant", "content": assistant_message})
            
            # Update chat display
            display_chat()
        except Exception as e:
            st.error(f"Error with AI Tutor API: {e}")
