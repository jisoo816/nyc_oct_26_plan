import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(
    page_title="NYC Trip Guide - Jungweon's Bachelorette 💍",
    page_icon="💍",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Hide default Streamlit header/footer for native app feel
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding: 0rem !important;
        margin: 0rem !important;
        max-width: 100% !important;
    }
    iframe {
        border: none !important;
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

html_path = Path("NYC_Bachelorette_Final_Flight_Linked.html")
if html_path.exists():
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    components.html(html_content, height=3600, scrolling=True)
else:
    st.error("HTML 파일을 찾을 수 없습니다.")