import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv() 

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="FinSolve QueryBot", page_icon="🤖")

# Session state initialization
if "auth" not in st.session_state:
    st.session_state.auth = None
    st.session_state.chat_history = []
    st.session_state.role = ""
    st.session_state.username = ""

st.title("🤖 FinSolve QueryBot")

# Sidebar logout and welcome info
if st.session_state.auth:
    with st.sidebar:
        st.markdown("## 👤 User Info")
        st.markdown(f"**Username:** {st.session_state.username}")
        st.markdown(f"**Role:** {st.session_state.role}")
        if st.button("🚪 Logout"):
            st.session_state.auth = None
            st.session_state.username = ""
            st.session_state.role = ""
            st.session_state.chat_history = []
            st.rerun()

# Login UI
if not st.session_state.auth:
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_clicked = st.button("Login")

    if login_clicked:
        try:
            # Send login request to FastAPI backend            
            response = requests.get(
                "{BACKEND_URL}/auth/login",
                auth=(username, password),
            )
            if response.status_code == 200:
                st.session_state.auth = (username, password)
                st.session_state.username = username
                st.session_state.role = response.json()["role"].capitalize()
                st.rerun()
            else:
                st.error("❌ Invalid credentials.")
        except requests.exceptions.RequestException:
            st.error("❌ Backend not reachable. Is FastAPI running?")
else:
    # Chat interface for authenticated users
    st.success(f"Welcome back, {st.session_state.username}! 👤 Role: {st.session_state.role}")
    st.subheader("💬 Chat with FinSolve")

    for role, msg in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(msg)

    # Checkbox to enable or disable history
    use_history = st.checkbox("Enable conversation history", value=False)
    user_input = st.chat_input("Type your question...")
    if user_input:
        with st.chat_message("user", avatar="🧑🏻‍💼"):
            st.markdown(user_input)

        # Store user message in session history
        st.session_state.chat_history.append(("user", user_input))

        with st.spinner("Generating response..."):
            try:
                chat_payload = {
                    "message": user_input,
                    "use_history": use_history,
                }

                # Add history if enabled and available
                if use_history:
                    chat_payload["history"] = [
                        {"user": st.session_state.chat_history[i][1], "ai": st.session_state.chat_history[i + 1][1]}
                        for i in range(0, len(st.session_state.chat_history) - 1, 2)
                        if st.session_state.chat_history[i][0] == "user"
                    ]

                # Send request to FastAPI /chat endpoint
                response = requests.post(
                    "{BACKEND_URL}/chat/",
                    json=chat_payload,
                    auth=st.session_state.auth,
                )
                
                # Parse response message and source documents
                bot_reply = response.json().get("response", "⚠️ Unexpected error in response.")
                sources = response.json().get("sources", [])
                if sources:
                    bot_reply += f"\n\n📄 **Sources:** " + ", ".join(sources)

            except requests.exceptions.RequestException:
                bot_reply = "❌ Could not connect to backend."

        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(bot_reply)
        st.session_state.chat_history.append(("assistant", bot_reply))