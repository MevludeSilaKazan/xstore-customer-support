"""
XStore Customer Support - Chat Interface
Gerçek chatbot deneyimi

Çalıştır: streamlit run app.py --server.port 8501
"""

import streamlit as st
from backend import ask, STORE, LANG

# Sayfa ayarları
st.set_page_config(
    page_title=f"{STORE['name']} Müşteri Destek",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS - Chat tarzı görünüm
st.markdown("""
<style>
    /* Ana container */
    .main {
        background-color: #f5f5f5;
    }
    
    /* Header */
    .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .chat-header h2 {
        margin: 0;
        font-size: 1.5rem;
    }
    
    .chat-header p {
        margin: 0.3rem 0 0 0;
        opacity: 0.9;
        font-size: 0.9rem;
    }
    
    /* Chat container */
    .chat-container {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
        max-height: 500px;
        overflow-y: auto;
    }
    
    /* Mesaj kutuları */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.8rem 1rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        margin-left: 20%;
        text-align: right;
    }
    
    .bot-message {
        background: #e8e8e8;
        color: #333;
        padding: 0.8rem 1rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
        word-wrap: break-word;
        white-space: pre-wrap;
    }
    
    .bot-message strong {
        color: #667eea;
    }
    
    /* Kategori badge */
    .category-badge {
        display: inline-block;
        background: #667eea20;
        color: #667eea;
        padding: 0.2rem 0.6rem;
        border-radius: 10px;
        font-size: 0.75rem;
        margin-bottom: 0.5rem;
    }
    
    /* Hızlı butonlar */
    .quick-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 1rem;
    }
    
    /* Input alanı */
    .stTextInput > div > div > input {
        border-radius: 25px !important;
        padding: 0.8rem 1.2rem !important;
    }
    
    /* Gönder butonu */
    .stButton > button {
        border-radius: 25px !important;
        padding: 0.5rem 2rem !important;
    }
    
    /* Sidebar */
    .store-info {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Session state - chat geçmişi
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Hoşgeldin mesajı
    welcome_msg = {
        "role": "assistant",
        "content": f"Merhaba! 👋 Ben {STORE['name']} asistanıyım.\n\nSize nasıl yardımcı olabilirim?",
        "category": None
    }
    st.session_state.messages.append(welcome_msg)

if "language" not in st.session_state:
    st.session_state.language = "auto"

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shopping-bag.png", width=60)
    st.title("⚙️ Ayarlar")
    
    lang_option = st.radio(
        "🌍 Dil / Language",
        ["🔄 Otomatik", "🇹🇷 Türkçe", "🇬🇧 English"],
        index=0
    )
    
    if "Türkçe" in lang_option:
        st.session_state.language = "tr"
    elif "English" in lang_option:
        st.session_state.language = "en"
    else:
        st.session_state.language = "auto"
    
    st.divider()
    
    st.markdown("### 🏪 Mağaza Bilgileri")
    st.markdown(f"""
    <div class="store-info">
    📍 <strong>{STORE['name']}</strong><br>
    🕐 {STORE['working_hours']}<br>
    📞 {STORE['phone']}<br>
    📧 {STORE['email']}<br>
    📸 {STORE['instagram']}
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    if st.button("🗑️ Sohbeti Temizle", use_container_width=True):
        st.session_state.messages = [{
            "role": "assistant",
            "content": f"Merhaba! 👋 Ben {STORE['name']} asistanıyım.\n\nSize nasıl yardımcı olabilirim?",
            "category": None
        }]
        st.rerun()

# Header
st.markdown(f"""
<div class="chat-header">
    <h2>🛒 {STORE['name']}</h2>
    <p>Müşteri Destek Asistanı</p>
</div>
""", unsafe_allow_html=True)

# Chat mesajlarını göster
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                {msg["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            category_html = ""
            if msg.get("category"):
                category_html = f'<span class="category-badge">{msg["category"]}</span><br>'
            
            st.markdown(f"""
            <div class="bot-message">
                {category_html}
                {msg["content"]}
            </div>
            """, unsafe_allow_html=True)

# Hızlı sorular
st.markdown("---")
quick_questions = [
    "👕 Tişört modelleri",
    "📦 Sipariş takibi",
    "🔄 İade nasıl yapılır?",
    "🎁 İndirim kodları",
    "📏 Beden tablosu"
]

cols = st.columns(len(quick_questions))
for i, q in enumerate(quick_questions):
    with cols[i]:
        if st.button(q, key=f"quick_{i}", use_container_width=True):
            # Butona tıklandığında soruyu gönder
            clean_q = q.split(" ", 1)[1] if " " in q else q  # Emojiyi kaldır
            st.session_state.pending_question = clean_q
            st.rerun()

# Bekleyen soru varsa işle
if "pending_question" in st.session_state:
    query = st.session_state.pending_question
    del st.session_state.pending_question
    
    # Kullanıcı mesajını ekle
    st.session_state.messages.append({
        "role": "user",
        "content": query
    })
    
    # Yanıt al
    lang = None if st.session_state.language == "auto" else st.session_state.language
    result = ask(query, language=lang)
    
    # Bot yanıtını ekle
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["response"],
        "category": result["category"]
    })
    
    st.rerun()

# Input alanı
st.markdown("---")
col1, col2 = st.columns([5, 1])

with col1:
    user_input = st.text_input(
        "Mesajınız",
        placeholder="Bir soru yazın... (Örn: M beden tişört var mı?)",
        label_visibility="collapsed",
        key="user_input"
    )

with col2:
    send_button = st.button("📤", type="primary", use_container_width=True)

# Mesaj gönder
if send_button and user_input:
    # Kullanıcı mesajını ekle
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Yanıt al
    with st.spinner(""):
        lang = None if st.session_state.language == "auto" else st.session_state.language
        result = ask(user_input, language=lang)
    
    # Bot yanıtını ekle
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["response"],
        "category": result["category"]
    })
    
    st.rerun()

# Enter ile gönderme (JavaScript)
st.markdown("""
<script>
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        const buttons = document.querySelectorAll('button');
        buttons.forEach(btn => {
            if (btn.innerText.includes('📤')) {
                btn.click();
            }
        });
    }
});
</script>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.8rem; margin-top: 2rem;">
    Powered by LangGraph & Groq AI
</div>
""", unsafe_allow_html=True)
