import streamlit as st
import openai
import time

# ========== 🔐 API Keys ==========
openai.api_key = st.secrets["OPENAI_API_KEY"]
assistant_id = st.secrets["ASSISTANT_ID"]

# ========== 📋 App UI ==========
st.set_page_config(page_title="FMP Code Generator", layout="centered")
st.title("📊 FMP Code Generator Assistant")
st.markdown("Enter a natural prompt and get Python code to pull financial data using the FMP **stable** API.")

user_prompt = st.text_area(
    "💬 Enter your request:",
    placeholder="e.g. Give me code to get AAPL's income statement"
)

if st.button("🔍 Generate Code"):
    if not user_prompt.strip():
        st.warning("Please enter a valid prompt.")
    else:
        with st.spinner("Asking your assistant..."):

            # 1. Create a thread
            thread = openai.beta.threads.create()

            # 2. Send the user's prompt
            openai.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_prompt
            )

            # 3. Run the assistant
            run = openai.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant_id
            )

            # 4. Poll until run is complete
            while run.status not in ("completed", "failed"):
                time.sleep(1)
                run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

            # 5. Get assistant's reply
            messages = openai.beta.threads.messages.list(thread_id=thread.id)
            assistant_reply = next((m for m in reversed(messages.data) if m.role == "assistant"), None)

            if assistant_reply:
                response = assistant_reply.content[0].text.value
                st.code(response, language="python")
                st.success("✅ Code generated! Copy and run it in your notebook or script.")
            else:
                st.error("❌ Assistant did not return a valid message.")
