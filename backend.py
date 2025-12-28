"""
XStore Customer Support Agent - Backend with Database
Veritabanından gerçek ürün bilgisi çeken versiyon
"""

import os
import re
from typing import TypedDict, Optional
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

# Database import
from database.db import (
    search_products as db_search_products, 
    check_stock, 
    get_products_by_category,
    get_product_stock,
    format_product_info
)

# Elasticsearch import
try:
    from database.elastic import search_products as es_search_products, check_connection
    ES_AVAILABLE, _ = check_connection()
except:
    ES_AVAILABLE = False

def search_products(query, lang="tr"):
    """Elasticsearch varsa onu kullan, yoksa PostgreSQL."""
    if ES_AVAILABLE:
        return es_search_products(query, max_results=5)
    return db_search_products(query, lang)

load_dotenv()

def get_llm():
    return ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# 🏪 MAĞAZA BİLGİLERİ
STORE = {
    "name": "XStore",
    "category": "Giyim & Moda",
    "return_days": 14,
    "return_free": True,
    "free_shipping_limit": 1200,
    "shipping_days": "2-4 iş günü",
    "shipping_days_en": "2-4 business days",
    "shipping_cost": 49.90,
    "working_hours": "09:00 - 18:00 (Hafta içi)",
    "working_hours_en": "09:00 - 18:00 (Weekdays)",
    "phone": "0850 XXX XX XX",
    "email": "destek@xstore.com",
    "instagram": "@xstore"
}

CATEGORIES = ["product", "order", "return", "payment", "account", "campaign", "general"]

class State(TypedDict):
    query: str
    language: str
    category: str
    sentiment: str
    response: str
    db_context: str  # Veritabanından gelen bilgi

# Veritabanı yardımcı fonksiyonları
def extract_product_query(query: str) -> dict:
    """Sorgudan ürün, beden, renk bilgisi çıkar."""
    query_lower = query.lower()
    
    # Beden çıkar
    size = None
    size_patterns = ['xxl', 'xl', 'xs', 's', 'm', 'l', '28', '30', '32', '34', '36', '38', '40', '42', '44']
    for s in size_patterns:
        if s in query_lower.split() or f" {s} " in f" {query_lower} ":
            size = s.upper()
            break
    
    # Renk çıkar
    color = None
    colors = {
        'siyah': 'Siyah', 'black': 'Siyah',
        'beyaz': 'Beyaz', 'white': 'Beyaz',
        'mavi': 'Mavi', 'blue': 'Mavi',
        'kırmızı': 'Kırmızı', 'red': 'Kırmızı',
        'yeşil': 'Yeşil', 'green': 'Yeşil',
        'gri': 'Gri', 'gray': 'Gri', 'grey': 'Gri',
        'lacivert': 'Lacivert', 'navy': 'Lacivert',
        'pembe': 'Pembe', 'pink': 'Pembe',
        'bej': 'Bej', 'beige': 'Bej',
        'haki': 'Haki', 'khaki': 'Haki'
    }
    for c_key, c_val in colors.items():
        if c_key in query_lower:
            color = c_val
            break
    
    return {"size": size, "color": color}


def get_db_context(query: str, lang: str = "tr") -> str:
    """Sorguya göre veritabanından bilgi çek."""
    query_lower = query.lower()
    context = ""
    
    # Ürün arama kelimeleri
    product_keywords = ['ürün', 'product', 'tişört', 't-shirt', 'tshirt', 'gömlek', 'shirt', 
                       'pantolon', 'pants', 'jean', 'elbise', 'dress', 'mont', 'jacket',
                       'sweatshirt', 'hoodie', 'ceket', 'blazer', 'etek', 'skirt',
                       'fiyat', 'price', 'kaç para', 'how much', 'ne kadar']
    
    # Stok arama kelimeleri
    stock_keywords = ['stok', 'stock', 'var mı', 'available', 'mevcut', 'kaldı mı', 
                     'beden', 'size', 'renk', 'color']
    
    # Stok sorgusu mu?
    is_stock_query = any(kw in query_lower for kw in stock_keywords)
    
    # Ürün/fiyat sorgusu mu?
    is_product_query = any(kw in query_lower for kw in product_keywords)
    
    if is_stock_query or is_product_query:
        # Ürün detaylarını çıkar
        details = extract_product_query(query)
        
        # Elasticsearch ile akıllı arama
        products = search_products(query, lang)
        
        if products:
            if ES_AVAILABLE:
                # Elasticsearch sonuçları
                if lang == "tr":
                    context = "📦 Bulunan ürünler:\n\n"
                else:
                    context = "📦 Found products:\n\n"
                
                for p in products[:3]:
                    context += f"• **{p['name']}** - {p['price']}₺\n"
                    if p.get('sizes'):
                        sizes_str = ', '.join(p['sizes'][:5])
                        if lang == "tr":
                            context += f"  Bedenler: {sizes_str}\n"
                        else:
                            context += f"  Sizes: {sizes_str}\n"
                    if p.get('colors'):
                        colors_str = ', '.join(list(set(p['colors']))[:5])
                        if lang == "tr":
                            context += f"  Renkler: {colors_str}\n"
                        else:
                            context += f"  Colors: {colors_str}\n"
                    stock_status = "✅ Stokta" if p.get('total_stock', 0) > 0 else "❌ Tükendi"
                    if lang == "en":
                        stock_status = "✅ In stock" if p.get('total_stock', 0) > 0 else "❌ Out of stock"
                    context += f"  {stock_status}\n\n"
            else:
                # PostgreSQL sonuçları (eski format)
                product = products[0]
                stock_info = get_product_stock(product['id'], lang)
                
                if details['size'] or details['color']:
                    filtered_stock = stock_info
                    if details['size']:
                        filtered_stock = [s for s in filtered_stock if s['size'].upper() == details['size']]
                    if details['color']:
                        filtered_stock = [s for s in filtered_stock if details['color'].lower() in s['color'].lower()]
                    
                    if filtered_stock:
                        context = format_product_info(product, filtered_stock, lang)
                    else:
                        if lang == "tr":
                            context = f"❌ {product['name']} ürününde "
                            if details['size']:
                                context += f"{details['size']} beden "
                            if details['color']:
                                context += f"{details['color']} renk "
                            context += "stokta yok.\n\n"
                            context += "Mevcut seçenekler:\n"
                        else:
                            context = f"❌ {product['name']} - "
                            if details['size']:
                                context += f"size {details['size']} "
                            if details['color']:
                                context += f"in {details['color']} "
                            context += "is not in stock.\n\n"
                            context += "Available options:\n"
                        
                        for s in stock_info[:5]:
                            if s['stock'] > 0:
                                context += f"  ✅ {s['size']} - {s['color']}: {s['stock']} adet\n"
                else:
                    context = format_product_info(product, stock_info, lang)
    
    return context


# 🇹🇷 TÜRKÇE PROMPTLAR
TR_PROMPTS = {
    "categorize": f"""Müşteri sorgusunu {STORE['name']} giyim mağazası için kategorize et.

KATEGORİLER:
- product: Ürün, beden, kumaş, renk, stok, fiyat
- order: Sipariş durumu, kargo, teslimat
- return: İade, değişim, para iadesi
- payment: Ödeme, fatura, taksit
- account: Hesap, şifre, üyelik
- campaign: İndirim, kupon, kampanya
- general: Genel sorular, iletişim

Sadece kategori kodunu yaz: {{query}}""",

    "sentiment": """Duygu analizi yap.

- Pozitif: Teşekkür, memnuniyet
- Nötr: Normal sorular (ÇOĞU MESAJ!)
- Negatif: SADECE küfür, hakaret, "rezalet", "dolandırıcı"

"istiyorum", "bekliyorum", "küçük geldi", "var mı" = NEGATİF DEĞİL!

Sadece yaz (Pozitif/Nötr/Negatif): {query}""",

    "product": f"""Sen {STORE['name']} müşteri destek asistanısın.

VERITABANINDAN GELEN BİLGİ:
{{db_context}}

BEDEN REHBERİ (eğer üstte bilgi yoksa):
- XS: 32-34 beden, göğüs 82-86cm
- S: 36-38 beden, göğüs 86-90cm
- M: 38-40 beden, göğüs 90-94cm
- L: 40-42 beden, göğüs 94-98cm
- XL: 42-44 beden, göğüs 98-102cm

KURALLAR:
- Veritabanından gelen bilgiyi kullan
- Fiyatları ve stok durumunu doğru aktar
- Stokta yoksa alternatif öner

Müşteri: {{query}}""",

    "order": f"""Sen {STORE['name']} müşteri destek asistanısın.

SİPARİŞ & KARGO:
- Siparişler 1-2 iş günü içinde kargoya verilir
- Teslimat: {STORE['shipping_days']}
- {STORE['free_shipping_limit']}₺ üzeri ücretsiz kargo
- Altında {STORE['shipping_cost']}₺ kargo ücreti
- Takip: SMS/email ile bildirilir
- Sipariş durumu: Hesabım > Siparişlerim

Müşteri: {{query}}""",

    "return": f"""Sen {STORE['name']} müşteri destek asistanısın.

İADE POLİTİKASI:
- Süre: {STORE['return_days']} gün
- Ücret: Ücretsiz (kargo bizden)
- Koşul: Etiketli, kullanılmamış, orijinal pakette
- İç giyim/mayo iade edilemez

İADE ADIMLAR:
1. Hesabım > Siparişlerim > İade Talebi
2. İade nedenini seç
3. Kargo kodunu al
4. Kargo şubesine teslim et
5. Para iadesi 3-5 iş günü

Müşteri: {{query}}""",

    "payment": f"""Sen {STORE['name']} müşteri destek asistanısın.

ÖDEME SEÇENEKLERİ:
- Kredi kartı (tek çekim + taksit)
- Banka kartı
- Havale/EFT
- Kapıda ödeme (+15₺)

TAKSİT:
- 100₺ üzeri: 3 taksit
- 300₺ üzeri: 6 taksit
- 500₺ üzeri: 9 taksit

FATURA: Email ile gönderilir, Hesabım > Siparişlerim'den indirilebilir.

Müşteri: {{query}}""",

    "account": f"""Sen {STORE['name']} müşteri destek asistanısın.

HESAP İŞLEMLERİ:
- Şifre sıfırlama: Giriş > Şifremi Unuttum
- Adres: Hesabım > Adreslerim
- Profil: Hesabım > Profil

ÜYELİK AVANTAJLARI:
- İlk alışverişte %10 indirim
- Özel kampanyalar
- Kolay sipariş takibi

Müşteri: {{query}}""",

    "campaign": f"""Sen {STORE['name']} müşteri destek asistanısın.

AKTİF KAMPANYALAR:
- Yeni üyelere %10 indirim (kod: HOSGELDIN)
- {STORE['free_shipping_limit']}₺ üzeri ücretsiz kargo
- Sezon sonu %50'ye varan indirim

KUPON: Sepette "Kupon Kodu" alanına gir. Her siparişte 1 kupon.

Müşteri: {{query}}""",

    "general": f"""Sen {STORE['name']} müşteri destek asistanısın.

BİLGİLER:
- Çalışma: {STORE['working_hours']}
- Tel: {STORE['phone']}
- Email: {STORE['email']}
- Instagram: {STORE['instagram']}

Müşteri: {{query}}""",

    "escalate": f"""⚠️ Değerli müşterimiz,

Yaşadığınız olumsuz deneyim için özür dileriz. Müşteri hizmetleri ekibimiz sizinle iletişime geçecektir.

Acil: {STORE['phone']}

{STORE['name']} Müşteri Hizmetleri"""
}

# 🇬🇧 ENGLISH PROMPTS
EN_PROMPTS = {
    "categorize": f"""Categorize this query for {STORE['name']} clothing store.

CATEGORIES:
- product: Size, fabric, color, stock, fit, price
- order: Order status, shipping, tracking, delivery
- return: Returns, exchanges, refunds
- payment: Payment, invoice, installments
- account: Account, password, membership
- campaign: Discounts, coupons, promotions
- general: Business hours, contact, other

Only write category code: {{query}}""",

    "sentiment": """Analyze sentiment.

- Positive: Thanks, praise, satisfaction
- Neutral: Normal questions (MOST MESSAGES!)
- Negative: ONLY insults, threats, "scam", "terrible", extreme anger

NOT negative: "want to return", "where is my order", "doesn't fit", "available?"

Only write (Positive/Neutral/Negative): {query}""",

    "product": f"""You are {STORE['name']} customer support assistant.

DATABASE INFO:
{{db_context}}

SIZE GUIDE (if no info above):
- XS: US 0-2, Chest 32-34" (82-86cm)
- S: US 4-6, Chest 34-35" (86-90cm)
- M: US 8-10, Chest 35-37" (90-94cm)
- L: US 10-12, Chest 37-39" (94-98cm)
- XL: US 14-16, Chest 39-40" (98-102cm)

RULES:
- Use database info when available
- Provide accurate prices and stock
- Suggest alternatives if out of stock

Customer: {{query}}""",

    "order": f"""You are {STORE['name']} customer support assistant.

ORDER & SHIPPING:
- Orders ship within 1-2 business days
- Delivery: {STORE['shipping_days_en']}
- Free shipping over {STORE['free_shipping_limit']}₺
- Under that: {STORE['shipping_cost']}₺ shipping
- Tracking via SMS/email
- Check: My Account > My Orders

Customer: {{query}}""",

    "return": f"""You are {STORE['name']} customer support assistant.

RETURN POLICY:
- Time: {STORE['return_days']} days
- Cost: FREE (we cover shipping)
- Condition: Tags on, unworn, original package
- Underwear/swimwear non-returnable

STEPS:
1. My Account > My Orders > Request Return
2. Select reason
3. Get shipping code
4. Drop at shipping point
5. Refund in 3-5 days

Customer: {{query}}""",

    "payment": f"""You are {STORE['name']} customer support assistant.

PAYMENT OPTIONS:
- Credit card (one-time + installments)
- Debit card
- Bank transfer
- Cash on delivery (+15₺)

INSTALLMENTS:
- Over 100₺: 3 installments
- Over 300₺: 6 installments
- Over 500₺: 9 installments

Customer: {{query}}""",

    "account": f"""You are {STORE['name']} customer support assistant.

ACCOUNT:
- Password reset: Login > Forgot Password
- Address: My Account > Addresses
- Profile: My Account > Profile

BENEFITS:
- 10% off first order
- Exclusive campaigns
- Easy order tracking

Customer: {{query}}""",

    "campaign": f"""You are {STORE['name']} customer support assistant.

ACTIVE CAMPAIGNS:
- New members: 10% off (code: WELCOME10)
- Free shipping over {STORE['free_shipping_limit']}₺
- End of season up to 50% off

COUPON: Enter at checkout. One per order.

Customer: {{query}}""",

    "general": f"""You are {STORE['name']} customer support assistant.

INFO:
- Hours: {STORE['working_hours_en']}
- Phone: {STORE['phone']}
- Email: {STORE['email']}
- Instagram: {STORE['instagram']}

Customer: {{query}}""",

    "escalate": f"""⚠️ Dear Customer,

We apologize for your experience. Our team will contact you shortly.

Immediate help: {STORE['phone']}

{STORE['name']} Customer Service"""
}

# Dil yapılandırması
LANG = {
    "tr": {
        "name": "Türkçe",
        "cat": {
            "product": "👕 Ürün & Beden",
            "order": "📦 Sipariş & Kargo",
            "return": "🔄 İade & Değişim",
            "payment": "💳 Ödeme & Fatura",
            "account": "🔐 Hesap & Üyelik",
            "campaign": "🎁 Kampanya & İndirim",
            "general": "ℹ️ Genel Bilgi"
        },
        "sent": {
            "positive": "😊 Pozitif",
            "neutral": "😐 Nötr",
            "negative": "😠 Negatif"
        },
        "prompts": TR_PROMPTS
    },
    "en": {
        "name": "English",
        "cat": {
            "product": "👕 Product & Size",
            "order": "📦 Order & Shipping",
            "return": "🔄 Return & Exchange",
            "payment": "💳 Payment & Invoice",
            "account": "🔐 Account",
            "campaign": "🎁 Deals & Discounts",
            "general": "ℹ️ General"
        },
        "sent": {
            "positive": "😊 Positive",
            "neutral": "😐 Neutral",
            "negative": "😠 Negative"
        },
        "prompts": EN_PROMPTS
    }
}

# Yardımcı fonksiyonlar
def norm_cat(c):
    c = c.lower().strip()
    m = {
        "product": "product", "ürün": "product", "beden": "product", "size": "product",
        "order": "order", "sipariş": "order", "kargo": "order", "shipping": "order",
        "return": "return", "iade": "return", "değişim": "return", "exchange": "return",
        "payment": "payment", "ödeme": "payment", "fatura": "payment", "taksit": "payment",
        "account": "account", "hesap": "account", "şifre": "account",
        "campaign": "campaign", "kampanya": "campaign", "indirim": "campaign",
        "general": "general", "genel": "general"
    }
    return m.get(c, "general")

def norm_sent(s):
    s = s.lower().strip()
    m = {
        "pozitif": "positive", "positive": "positive",
        "nötr": "neutral", "neutral": "neutral",
        "negatif": "negative", "negative": "negative"
    }
    return m.get(s, "neutral")

# Node fonksiyonları
def detect_language(state: State) -> State:
    if state.get("language") in ["tr", "en"]:
        return {"language": state["language"]}
    prompt = ChatPromptTemplate.from_template(
        "Is this Turkish or English? Reply ONLY 'tr' or 'en': {query}"
    )
    res = (prompt | get_llm()).invoke({"query": state["query"]}).content.strip().lower()
    return {"language": res if res in ["tr", "en"] else "tr"}

def categorize(state: State) -> State:
    lang = state.get("language", "tr")
    prompt = ChatPromptTemplate.from_template(LANG[lang]["prompts"]["categorize"])
    res = (prompt | get_llm()).invoke({"query": state["query"]}).content
    return {"category": norm_cat(res)}

def analyze_sentiment(state: State) -> State:
    lang = state.get("language", "tr")
    prompt = ChatPromptTemplate.from_template(LANG[lang]["prompts"]["sentiment"])
    res = (prompt | get_llm()).invoke({"query": state["query"]}).content
    return {"sentiment": norm_sent(res)}

def fetch_db_context(state: State) -> State:
    """Veritabanından ilgili bilgiyi çek."""
    lang = state.get("language", "tr")
    db_context = get_db_context(state["query"], lang)
    return {"db_context": db_context}

def handle_product(state: State) -> State:
    lang = state.get("language", "tr")
    prompt = ChatPromptTemplate.from_template(LANG[lang]["prompts"]["product"])
    db_context = state.get("db_context", "")
    return {"response": (prompt | get_llm()).invoke({
        "query": state["query"],
        "db_context": db_context if db_context else "Veritabanında bilgi bulunamadı."
    }).content}

def handle_order(state: State) -> State:
    lang = state.get("language", "tr")
    prompt = ChatPromptTemplate.from_template(LANG[lang]["prompts"]["order"])
    return {"response": (prompt | get_llm()).invoke({"query": state["query"]}).content}

def handle_return(state: State) -> State:
    lang = state.get("language", "tr")
    prompt = ChatPromptTemplate.from_template(LANG[lang]["prompts"]["return"])
    return {"response": (prompt | get_llm()).invoke({"query": state["query"]}).content}

def handle_payment(state: State) -> State:
    lang = state.get("language", "tr")
    prompt = ChatPromptTemplate.from_template(LANG[lang]["prompts"]["payment"])
    return {"response": (prompt | get_llm()).invoke({"query": state["query"]}).content}

def handle_account(state: State) -> State:
    lang = state.get("language", "tr")
    prompt = ChatPromptTemplate.from_template(LANG[lang]["prompts"]["account"])
    return {"response": (prompt | get_llm()).invoke({"query": state["query"]}).content}

def handle_campaign(state: State) -> State:
    lang = state.get("language", "tr")
    prompt = ChatPromptTemplate.from_template(LANG[lang]["prompts"]["campaign"])
    return {"response": (prompt | get_llm()).invoke({"query": state["query"]}).content}

def handle_general(state: State) -> State:
    lang = state.get("language", "tr")
    prompt = ChatPromptTemplate.from_template(LANG[lang]["prompts"]["general"])
    return {"response": (prompt | get_llm()).invoke({"query": state["query"]}).content}

def escalate(state: State) -> State:
    lang = state.get("language", "tr")
    return {"response": LANG[lang]["prompts"]["escalate"]}

def route(state: State) -> str:
    if state["sentiment"] == "negative":
        return "escalate"
    return f"handle_{state['category']}"

# Graph oluştur
def build_graph():
    wf = StateGraph(State)

    wf.add_node("detect_language", detect_language)
    wf.add_node("categorize", categorize)
    wf.add_node("analyze_sentiment", analyze_sentiment)
    wf.add_node("fetch_db_context", fetch_db_context)
    wf.add_node("handle_product", handle_product)
    wf.add_node("handle_order", handle_order)
    wf.add_node("handle_return", handle_return)
    wf.add_node("handle_payment", handle_payment)
    wf.add_node("handle_account", handle_account)
    wf.add_node("handle_campaign", handle_campaign)
    wf.add_node("handle_general", handle_general)
    wf.add_node("escalate", escalate)

    wf.add_edge("detect_language", "categorize")
    wf.add_edge("categorize", "analyze_sentiment")
    wf.add_edge("analyze_sentiment", "fetch_db_context")
    wf.add_conditional_edges("fetch_db_context", route, {
        "handle_product": "handle_product",
        "handle_order": "handle_order",
        "handle_return": "handle_return",
        "handle_payment": "handle_payment",
        "handle_account": "handle_account",
        "handle_campaign": "handle_campaign",
        "handle_general": "handle_general",
        "escalate": "escalate"
    })

    for cat in CATEGORIES:
        wf.add_edge(f"handle_{cat}", END)
    wf.add_edge("escalate", END)

    wf.set_entry_point("detect_language")
    return wf.compile()

# App'i oluştur
app = build_graph()

def ask(query: str, language: str = None):
    """Müşteri sorusunu yanıtla ve sonucu döndür."""
    state = {"query": query}
    if language:
        state["language"] = language
    
    r = app.invoke(state)
    lang = r["language"]
    
    return {
        "query": query,
        "language": LANG[lang]["name"],
        "language_code": lang,
        "category": LANG[lang]["cat"][r["category"]],
        "category_code": r["category"],
        "sentiment": LANG[lang]["sent"][r["sentiment"]],
        "sentiment_code": r["sentiment"],
        "response": r["response"],
        "db_context": r.get("db_context", "")
    }


if __name__ == "__main__":
    print(f"🛒 {STORE['name']} Müşteri Destek Asistanı (Veritabanı Entegreli)")
    print("=" * 60)
    
    # Test sorguları
    test_queries = [
        "Siyah tişört var mı?",
        "M beden sweatshirt fiyatı ne kadar?",
        "Hangi montlar var?",
    ]
    
    for q in test_queries:
        print(f"\n👤 Müşteri: {q}")
        result = ask(q)
        print(f"🏷️ Kategori: {result['category']}")
        print(f"🤖 Asistan: {result['response'][:200]}...")
        print("-" * 40)
