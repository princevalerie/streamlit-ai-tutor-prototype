import streamlit as st
import subprocess
import tempfile
import os
import openai

# Set your OpenAI API key from sidebar input
api_key_input = st.sidebar.text_input("Masukkan OpenAI API Key Anda:", type="password")
if api_key_input:
    openai.api_key = api_key_input
else:
    st.sidebar.warning("Silakan masukkan API Key Anda untuk menggunakan AI Tutor.")
    st.stop()

st.set_page_config(page_title="AI Tutor Academy", layout="wide")

# Initialize session state for AI chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are an AI tutor that helps students learn Python. Provide clear, concise, and helpful explanations."}
    ]

# Sample question for demonstration
sample_question = """
Tulis sebuah fungsi Python yang menerima sebuah list integer dan mengembalikan jumlah elemen positif di dalamnya. Contoh: input [1, -2, 3, 4, -5] mengembalikan 3.
"""

# Layout with two columns: left for question & terminal, right for AI tutor
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Soal dan Terminal Python")
    st.subheader("Soal:")
    st.code(sample_question, language="python")

    # Code editor
    code = st.text_area("Tulis kode Python di sini:", height=200, value="""def count_positive(numbers):
    # Mulai tulis kode di sini
    pass

# Contoh penggunaan:
# print(count_positive([1, -2, 3, 4, -5]))  # Output: 3
""")

    # Run button
    if st.button("Jalankan Kode"):
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
            st.error("Eksekusi kode melebihi batas waktu.")
        finally:
            # Cleanup temporary file
            os.remove(tmp_file_path)

with col2:
    st.header("AI Tutor")
    # Display chat history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"**Anda:** {msg['content']}")
        elif msg["role"] == "assistant":
            st.markdown(f"**Tutor:** {msg['content']}")

    # User input for AI tutor
    user_input = st.text_input("Tanya Tutor tentang soal atau kode Anda:")
    if st.button("Kirim", key="send_ai") and user_input:
        # Append user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        # Call OpenAI Chat API
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.messages
            )
            assistant_message = response.choices[0].message["content"]
            # Append assistant message
            st.session_state.messages.append({"role": "assistant", "content": assistant_message})
        except Exception as e:
            st.error(f"Terjadi kesalahan dengan API AI: {e}")

        # Rerun to display updated chat
        st.experimental_rerun()
