import streamlit as st
import base64
from db_config import verify_user, add_user
from streamlit_extras.switch_page_button import switch_page

#st.set_page_config(page_title="Login - Stock Market Dashboard", layout="wide")

# ✅ Function to Set Background Image
def set_background(image_file):
    with open(image_file, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode()

    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded_string}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ✅ Set Background Image
set_background("pages/image.jpg")  # Ensure "image.jpg" exists in the same directory

# ✅ Ensure session state is initialized
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# 🚀 **Login UI Layout**
st.markdown("<h1 style='text-align: center; color: white;'>🔐 Login Page</h1>", unsafe_allow_html=True)

option = st.radio("Select an option:", ["Login", "Sign Up"])

if option == "Login":
    username = st.text_input("Username:", key="login_username")
    password = st.text_input("Password:", type="password", key="login_password")

    if st.button("Login"):
        if verify_user(username, password):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.success("Login successful! Redirecting...")
            st.rerun()  # ✅ Refresh the app
        else:
            st.error("Invalid username or password")

elif option == "Sign Up":
    new_username = st.text_input("Create Username:", key="signup_username")
    new_password = st.text_input("Create Password:", type="password", key="signup_password")

    if st.button("Sign Up"):
        if add_user(new_username, new_password):
            st.success("Account created successfully! Please login.")
        else:
            st.error("Username already exists. Choose a different one.")

# ✅ If user is authenticated, show a "Go to Dashboard" button
if st.session_state.authenticated:
    st.markdown("[Go to Dashboard](app.py)")
    st.switch_page("app.py")



# 🚀 Add Logout Button

