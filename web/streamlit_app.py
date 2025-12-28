"""
XStore Customer Support - Streamlit Web Interface
Run with: streamlit run web/streamlit_app.py
"""

import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.agents.support_agent import ask, LANG
from config.store_config import STORE

# Page config
st.set_page_config(
    page_title=f"{STORE['name']} Müşteri Destek",
    page_icon="🛒",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .response-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    .info-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 0.25rem;
    }
    .category-badge { background-color: #e3f2fd; color: #1976d2; }
    .sentiment-badge { background-color: #f3e5f5; color: #7b1fa2; }
    .language-badge { background-color: #e8f5e9; color: #388e3c; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown(f"""
<div class="main-header">
    <h1>🛒 {STORE['name']}</h1>
    <p>Müşteri Destek Asistanı | Customer Support</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Ayarlar / Settings")
    
    language_option = st.selectbox(
        "🌍 Dil / Language",
        ["Otomatik / Auto", "🇹🇷 Türkçe", "🇬🇧 English"]
    )
    
    st.divider()
    
    st.header("🏪 Mağaza Bilgileri")
    st.write(f"**İade:** {STORE['return_days']} gün, ücretsiz")
    st.write(f"**Kargo:** {STORE['free_shipping_limit']}₺ üzeri ücretsiz")
    st.write(f"**Teslimat:** {STORE['shipping_days']}")
    st.write(f"**Tel:** {STORE['phone']}")
    
    st.divider()
    
    st.header("📂 Kategoriler")
    for code, name in LANG["tr"]["cat"].items():
        st.write(name)

# Main area
st.subheader("💬 Nasıl yardımcı olabilirim?")

# Query input
query = st.text_area(
    "Sorunuzu yazın / Write your question:",
    placeholder="Örnek: Siparişim ne zaman gelir? / Example: What is your return policy?",
    height=100
)

# Submit button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    submit = st.button("🚀 Gönder / Send", use_container_width=True, type="primary")

# Process query
if submit and query:
    # Determine language
    lang_code = None
    if language_option == "🇹🇷 Türkçe":
        lang_code = "tr"
    elif language_option == "🇬🇧 English":
        lang_code = "en"
    
    with st.spinner("🤔 Düşünüyorum... / Thinking..."):
        try:
            result = ask(query, language=lang_code)
            
            # Display badges
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"<span class='info-badge language-badge'>🌍 {result['language']}</span>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<span class='info-badge category-badge'>{result['category']}</span>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<span class='info-badge sentiment-badge'>{result['sentiment']}</span>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Display response
            st.markdown(f"""
            <div class="response-box">
                <h4>🤖 {STORE['name']} Asistan:</h4>
                <p>{result['response']}</p>
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ Bir hata oluştu: {str(e)}")

elif submit and not query:
    st.warning("⚠️ Lütfen bir soru yazın / Please write a question")

# Example queries
st.markdown("---")
st.subheader("💡 Örnek Sorular / Example Questions")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**🇹🇷 Türkçe:**")
    examples_tr = [
        "M beden tişört alacağım, kalıbı nasıl?",
        "Siparişim ne zaman gelir?",
        "Ürünü iade etmek istiyorum",
        "İndirim kodu var mı?",
        "Taksitle ödeme yapabilir miyim?"
    ]
    for ex in examples_tr:
        if st.button(ex, key=f"tr_{ex}"):
            st.session_state.query = ex
            st.rerun()

with col2:
    st.markdown("**🇬🇧 English:**")
    examples_en = [
        "What size should I get?",
        "When will my order arrive?",
        "I want to return this item",
        "Do you have any discount codes?",
        "What is your return policy?"
    ]
    for ex in examples_en:
        if st.button(ex, key=f"en_{ex}"):
            st.session_state.query = ex
            st.rerun()

# Footer
st.markdown("---")
st.markdown(
    f"<center>Made with ❤️ using LangGraph & Streamlit | {STORE['name']} © 2024</center>",
    unsafe_allow_html=True
)
