import streamlit as st
import openai
import time

# ========== 🔐 Load API key & Assistant ==========
openai.api_key = st.secrets["OPENAI_API_KEY"]
assistant_id = st.secrets["ASSISTANT_ID"]

st.set_page_config(page_title="FMP Code Generator", layout="centered")
st.title("📊 FMP Code Generator Assistant")
st.markdown("Enter a natural prompt and receive Python code that pulls data from [Financial Modeling Prep](https://financialmodelingprep.com/developer/docs/).")

# ========== 📥 User Input ==========
user_prompt = st.text_area(
    "💬 Enter your request:",
    placeholder="e.g. Give me code to pull AAPL's income statement"
)

if st.button("🔍 Generate Code"):
    if not user_prompt.strip():
        st.warning("Please enter a prompt.")
    else:
        with st.spinner("Querying your assistant..."):
            # Step 1: Start a thread
            thread = openai.beta.threads.create()

            # Step 2: Send the prompt
            openai.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_prompt
            )

            # Step 3: Run the assistant
            run = openai.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant_id
            )

            # Step 4: Poll for completion
            while run.status not in ("completed", "failed"):
                time.sleep(1)
                run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

            # Step 5: Get assistant's message
            messages = openai.beta.threads.messages.list(thread_id=thread.id)
            assistant_reply = next((msg for msg in reversed(messages.data) if msg.role == "assistant"), None)

            if assistant_reply:
                response = assistant_reply.content[0].text.value
                st.code(response, language="python")
            else:
                st.error("Assistant returned no response.")
