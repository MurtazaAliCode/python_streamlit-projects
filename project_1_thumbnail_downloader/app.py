import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# Configure page
st.set_page_config(page_title="YouTube Thumbnail Downloader", layout="wide")

# Session state for history
if "download_history" not in st.session_state:
    st.session_state.download_history = []

# ====== Custom CSS for Styling ======
st.markdown("""
    <style>
    body {
        background-color: #f5f7fa;
    }
    .main {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 2rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        font-weight: bold;
        border-radius: 8px;
    }
    .stButton>button:hover {
        background-color: #e63946;
        color: #fff;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar for download history
# Sidebar for download history with Clear button
with st.sidebar:
    st.title("📜 Download History")

    # Clear button
    if st.button("🧹 Clear History"):
        st.session_state.download_history.clear()
        st.success("History cleared!")

    if st.session_state.download_history:
        for item in reversed(st.session_state.download_history):
            st.markdown(
                f"🔸 **{item['file_name']}**\n\n"
                f"📽 Video ID: `{item['video_id']}`\n"
                f"📏 Quality: `{item['quality']}`\n---"
            )
    else:
        st.info("No downloads yet.")


# Main Title
st.markdown(
    "<h1 style='text-align: center; color: #ff4b4b;'>📸 YouTube Thumbnail Downloader</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #444;'>Download high-quality YouTube thumbnails instantly.</p>",
    unsafe_allow_html=True,
)

# Input section
st.markdown("---")
with st.container():
    col1, col2 = st.columns([3, 2])
    with col1:
        video_url = st.text_input("🔗 YouTube Video URL:")
    with col2:
        custom_name = st.text_input("📝 Custom File Name (optional):", value="thumbnail")

    quality = st.selectbox("📏 Select Thumbnail Quality:", [
        "High (maxresdefault)", "Medium (mqdefault)", "Standard (sddefault)", "Low (hqdefault)"
    ])

quality_map = {
    "High (maxresdefault)": "maxresdefault",
    "Medium (mqdefault)": "mqdefault",
    "Standard (sddefault)": "sddefault",
    "Low (hqdefault)": "hqdefault"
}

def extract_video_id(url):
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    elif "youtube.com/watch?v=" in url:
        return url.split("v=")[1].split("&")[0]
    else:
        return None

# Thumbnail Processing
if video_url:
    video_id = extract_video_id(video_url)
    if video_id:
        selected_quality = quality_map[quality]
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/{selected_quality}.jpg"
        response = requests.get(thumbnail_url)

        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))

            st.markdown("### 🔍 Thumbnail Preview")
            st.image(image, use_column_width=True, caption=f"{selected_quality} Quality")

            filename_clean = custom_name.strip().replace(" ", "_") or video_id
            file_name = f"{filename_clean}_{selected_quality}.jpg"

            st.download_button(
                label="📥 Download Thumbnail",
                data=response.content,
                file_name=file_name,
                mime="image/jpeg"
            )

            st.session_state.download_history.append({
                "video_id": video_id,
                "quality": selected_quality,
                "file_name": file_name
            })
        else:
            st.error("❌ Thumbnail not found for selected quality.")
    else:
        st.error("⚠️ Invalid YouTube URL.")
