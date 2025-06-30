import streamlit as st
import requests

st.set_page_config(page_title="FinSolve QueryBot", page_icon="🤖")
st.title("🤖 FinSolve QueryBot")

# Session state initialization
if "auth" not in st.session_state:
    st.session_state.auth = None
    st.session_state.chat_history = []
    st.session_state.role = ""
    st.session_state.username = ""

# Login UI
if not st.session_state.auth:
    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    login_clicked = st.button("Login")

    if login_clicked:
        try:
            response = requests.get(
                "http://127.0.0.1:8000/auth/login",
                auth=(username, password),
                timeout=3
            )
            if response.status_code == 200:
                st.session_state.auth = (username, password)
                st.session_state.username = username
                st.session_state.role = response.json()["role"].capitalize()
                st.rerun()  # go directly to chat UI
            else:
                st.error("❌ Invalid credentials.")
        except requests.exceptions.RequestException:
            st.error("❌ Backend not reachable. Is FastAPI running?")
else:
    st.success(f"Welcome back, {st.session_state.username}!     👤 Role: {st.session_state.role}")

    if st.button("Logout"):
        st.session_state.auth = None
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.chat_history = []
        st.rerun()

    st.subheader("💬 Chat with FinSolve")

    for role, msg in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(msg)

    user_input = st.chat_input("Type your question...")
    if user_input:
        with st.chat_message("user",avatar="🧑🏻‍💼"):
            st.markdown(user_input)
        st.session_state.chat_history.append(("user", user_input))

        with st.spinner("Generating response..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/chat/",
                    json={"message": user_input},
                    auth=st.session_state.auth,
                )
                bot_reply = response.json().get("response", "⚠️ Unexpected error in response.")
            except requests.exceptions.RequestException:
                bot_reply = "❌ Could not connect to backend."

        with st.chat_message("assistant",avatar="🤖"):
            st.markdown(bot_reply)
        st.session_state.chat_history.append(("assistant", bot_reply))
