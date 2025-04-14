import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import re

# Set page config
st.set_page_config(page_title="Instagram DP Downloader", layout="wide")

# History state
if "dp_history" not in st.session_state:
    st.session_state.dp_history = []

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
    }
    .stButton>button:hover {
        background-color: #e63946;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar history
with st.sidebar:
    st.title("📜 Download History")
    if st.button("🧹 Clear History"):
        st.session_state.dp_history.clear()
        st.success("History cleared!")

    if st.session_state.dp_history:
        for item in reversed(st.session_state.dp_history):
            st.markdown(
                f"🔸 **{item['file_name']}**\n\n"
                f"👤 Username: `{item['username']}`\n"
                f"📸 Size: `{item['size']}`\n---"
            )
    else:
        st.info("No downloads yet.")

# App title
st.markdown(
    "<h1 style='text-align: center; color: #ff4b4b;'>📷 Instagram Profile Picture Downloader</h1>",
    unsafe_allow_html=True,
)

# Input section
st.markdown("---")
col1, col2 = st.columns([3, 2])
with col1:
    username = st.text_input("🔎 Instagram Username (without @):")
with col2:
    custom_name = st.text_input("📝 Custom File Name (optional):", value="instagram_dp")

# Function to get profile picture URL
def get_instagram_profile_pic(username):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    url = f"https://www.instagram.com/{username}/"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        match = re.search(r'"profile_pic_url_hd":"([^"]+)"', response.text)
        if match:
            return match.group(1).replace("\\u0026", "&")
    return None

# Processing
if username:
    st.markdown("### 🔍 Fetching profile picture...")
    img_url = get_instagram_profile_pic(username)

    if img_url:
        img_response = requests.get(img_url)
        if img_response.status_code == 200:
            img = Image.open(BytesIO(img_response.content))

            st.image(img, caption=f"@{username}", use_column_width=True)
            filename_clean = custom_name.strip().replace(" ", "_") or username
            file_name = f"{filename_clean}.jpg"

            st.download_button(
                label="📥 Download Profile Picture",
                data=img_response.content,
                file_name=file_name,
                mime="image/jpeg"
            )

            st.session_state.dp_history.append({
                "username": username,
                "file_name": file_name,
                "size": f"{img.width}x{img.height}"
            })
        else:
            st.error("❌ Failed to load image.")
    else:
        st.error("⚠️ Could not fetch profile picture. Username may be private or incorrect.")
