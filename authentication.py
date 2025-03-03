import streamlit as st
from database import execute_query, fetch_data, hash_password, generate_salt

# Function to register a new user securely
def signup(username, password):
    existing_user = fetch_data("SELECT username FROM users WHERE username=?", (username,))
    
    if existing_user:
        return False  # User already exists

    salt = generate_salt()
    hashed_password = hash_password(password, salt)
    
    execute_query("INSERT INTO users (username, password, salt) VALUES (?, ?, ?)", (username, hashed_password, salt))
    
    # 🔥 Ensure the user was added successfully before returning True
    user_check = fetch_data("SELECT username FROM users WHERE username=?", (username,))
    return bool(user_check)

# Function to verify user login
def login(username, password):
    user = fetch_data("SELECT password, salt FROM users WHERE username=?", (username,))
    
    if user:
        stored_hash = user[0]["password"]  # ✅ Extract by key
        salt = user[0]["salt"]  # ✅ Extract by key
        
        if stored_hash == hash_password(password, salt):
            return True
    return False

# Streamlit UI for Authentication
def authentication_ui():
    st.sidebar.title("🔑 Get Started")

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.session_state["guest_conversions"] = 0  # Track guest conversions

    if not st.session_state["logged_in"]:
        action = st.sidebar.radio("Choose Action", ["Login", "Signup"])
        
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")

        if action == "Signup":
            if st.sidebar.button("Sign Up"):
                if signup(username, password):
                    st.sidebar.success("✅ Account created! Please log in.")
                else:
                    st.sidebar.error("⚠ Username already exists!")

        elif action == "Login":
            if st.sidebar.button("Login"):
                if login(username, password):
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.sidebar.success(f"✅ Welcome, {username}!")
                    st.rerun()  # 🔥 Ensure UI updates instantly
                else:
                    st.sidebar.error("⚠ Invalid credentials!")
    else:
        st.sidebar.write(f"**Welcome, {st.session_state['username']}!**")
        if st.sidebar.button("Logout"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = None
            st.session_state["guest_conversions"] = 0
            st.rerun()  # 🔥 Ensure UI updates instantly
