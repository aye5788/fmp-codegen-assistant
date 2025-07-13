import streamlit as st
import openai
import time

# === API Keys ===
openai.api_key = st.secrets["OPENAI_API_KEY"]
assistant_id = st.secrets["ASSISTANT_ID"]

# === App UI ===
st.set_page_config(page_title="FMP Code Generator", layout="centered")
st.title("📊 FMP Code Generator Assistant")
st.markdown("Enter your request and get back ready-to-use Python code using the FMP **stable** API.")

user_prompt = st.text_area(
    "💬 Enter your request:",
    placeholder="e.g. Give me code to get AAPL's quarterly income statement"
)

if st.button("🔍 Generate Code"):
    if not user_prompt.strip():
        st.warning("Please enter a valid prompt.")
    else:
        with st.spinner("Working..."):

            # Create a thread & send message
            thread = openai.beta.threads.create()
            openai.beta.threads.messages.create(thread_id=thread.id, role="user", content=user_prompt)
            run = openai.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id)

            # Poll for completion
            while run.status not in ("completed", "failed"):
                time.sleep(1)
                run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

            # Get assistant reply
            messages = openai.beta.threads.messages.list(thread_id=thread.id)
            assistant_reply = next((m for m in reversed(messages.data) if m.role == "assistant"), None)

            if assistant_reply:
                code_output = assistant_reply.content[0].text.value

                # Display formatted code block
                st.code(code_output, language="python")

                # Copy-to-clipboard workaround (hidden text area + JS)
                st.text_area("📋 Copy below manually if needed:", code_output, height=200)

                st.markdown("""
                    <button onclick="navigator.clipboard.writeText(document.querySelector('textarea').value)"
                            style="padding:8px 16px; background-color:#4CAF50; color:white; border:none; border-radius:5px; cursor:pointer;">
                        📋 Copy to Clipboard
                    </button>
                    """, unsafe_allow_html=True)
            else:
                st.error("❌ Assistant did not return a valid message.")
