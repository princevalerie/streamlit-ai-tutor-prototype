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
        if not code.strip():
            st.error("Please enter some code to run.")
        else:
            # Save code to a temporary file and run it
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode='w', encoding='utf-8') as tmp_file:
                tmp_file.write(code)
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
                    if result.stdout.strip():
                        st.code(result.stdout)
                    else:
                        st.info("Code executed successfully with no output.")
                else:
                    st.subheader("Error:")
                    st.code(result.stderr)
            except subprocess.TimeoutExpired:
                st.error("Code execution exceeded the time limit.")
            except Exception as e:
                st.error(f"Error executing code: {str(e)}")
            finally:
                # Cleanup temporary file
                try:
                    os.remove(tmp_file_path)
                except:
                    pass  # Ignore cleanup errors

with col2:
    st.header("AI Tutor")
    
    # Function to display chat history
    def display_chat():
        for msg in st.session_state.messages:
            if msg.get("author") == "user":
                st.markdown(f"**You:** {msg['content']}")
            elif msg.get("author") == "assistant":
                st.markdown(f"**Tutor:** {msg['content']}")
            # Skip system messages in display

    # Display chat history
    display_chat()

    # User input for AI tutor
    if api_key_input:  # Only show input if API key is provided
        user_input = st.text_input("Ask the Tutor about the question or your code:")
        if st.button("Send", key="send_ai") and user_input.strip():
            # Append user message
            st.session_state.messages.append({"author": "user", "content": user_input})
            
            # Call Google Generative AI API
            try:
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                # Prepare conversation history for the API
                conversation_history = []
                system_instruction = ""
                
                # Extract system instruction
                for msg in st.session_state.messages:
                    if msg["author"] == "system":
                        system_instruction = msg["content"]
                        break
                
                # Build conversation history (skip system messages)
                for msg in st.session_state.messages:
                    if msg["author"] == "system":
                        continue
                    elif msg["author"] == "user":
                        conversation_history.append({"role": "user", "parts": [{"text": msg["content"]}]})
                    elif msg["author"] == "assistant":
                        conversation_history.append({"role": "model", "parts": [{"text": msg["content"]}]})
                
                # Add system instruction to the first user message if it exists
                if conversation_history and system_instruction:
                    first_user_msg = conversation_history[0]
                    if first_user_msg["role"] == "user":
                        original_text = first_user_msg["parts"][0]["text"]
                        first_user_msg["parts"][0]["text"] = f"{system_instruction}\n\nUser question: {original_text}"
                
                # Generate response
                response = model.generate_content(conversation_history)
                
                if response.text:
                    assistant_message = response.text
                    st.session_state.messages.append({"author": "assistant", "content": assistant_message})
                    st.rerun()  # Refresh to show new message
                else:
                    st.error("No response received from the AI model.")
                    
            except Exception as e:
                st.error(f"Error with AI Tutor API: {str(e)}")
                # Remove the user message if API call failed
                if st.session_state.messages and st.session_state.messages[-1]["author"] == "user":
                    st.session_state.messages.pop()
    else:
        st.info("Enter your API key to start chatting with the AI Tutor.")
