import streamlit as st
import requests

st.set_page_config(page_title="FinSolve Chatbot", page_icon="🤖")
st.title("🔐 FinSolve Internal Chatbot")

# Session state for login
if "auth" not in st.session_state:
    st.session_state.auth = None
    st.session_state.username = ""
    st.session_state.password = ""
    st.session_state.chat_history = []

# Login UI
if not st.session_state.auth:
    st.subheader("🔑 Login")
    st.session_state.username = st.text_input("Username")
    st.session_state.password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            res = requests.get(
                "http://localhost:8000/auth/login",
                auth=(st.session_state.username, st.session_state.password),
            )
            if res.status_code == 200:
                st.session_state.auth = (st.session_state.username, st.session_state.password)
                st.success(f"Logged in as {res.json()['role'].capitalize()}")
            else:
                st.error("Invalid credentials")
        except:
            st.error("Backend not reachable. Is FastAPI running?")
else:
    st.success(f"Welcome back, {st.session_state.username}!")

    # Chat UI
    st.subheader("💬 Ask Your Question")

    for role, msg in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(msg)

    user_input = st.chat_input("Type your question...")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.chat_history.append(("user", user_input))

        with st.spinner("Generating response..."):
            try:
                response = requests.post(
                    "http://localhost:8000/chat/",
                    json={"message": user_input},
                    auth=st.session_state.auth
                )
                bot_reply = response.json().get("response", "Error")
            except:
                bot_reply = "❌ Failed to connect to backend."

        with st.chat_message("assistant"):
            st.markdown(bot_reply)
        st.session_state.chat_history.append(("assistant", bot_reply))
