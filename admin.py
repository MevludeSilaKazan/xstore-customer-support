"""
XStore Admin Paneli
Ürün ve stok yönetimi

Çalıştır: streamlit run admin.py
"""

import streamlit as st
from database.db import get_connection

# Sayfa ayarları
st.set_page_config(
    page_title="XStore Admin",
    page_icon="⚙️",
    layout="wide"
)

# Basit şifre koruması
def check_password():
    """Şifre kontrolü."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown("## 🔐 Admin Girişi")
        password = st.text_input("Şifre:", type="password")
        if st.button("Giriş"):
            if password == "admin123":  # Gerçek uygulamada .env'den al
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Yanlış şifre!")
        return False
    return True

# Veritabanı fonksiyonları
def get_all_products():
    """Tüm ürünleri getir."""
    sql = """
    SELECT p.id, p.name, c.name as category, p.price, p.material, p.description
    FROM products p
    JOIN categories c ON p.category_id = c.id
    ORDER BY p.id
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            return rows

def get_all_categories():
    """Tüm kategorileri getir."""
    sql = "SELECT id, name, name_en FROM categories ORDER BY id"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

def get_product_stock(product_id):
    """Ürün stokunu getir."""
    sql = """
    SELECT id, size, color, stock 
    FROM product_stock 
    WHERE product_id = %s
    ORDER BY size, color
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (product_id,))
            return cur.fetchall()

def get_low_stock_products(threshold=10):
    """Düşük stoklu ürünleri getir."""
    sql = """
    SELECT p.name, ps.size, ps.color, ps.stock
    FROM product_stock ps
    JOIN products p ON ps.product_id = p.id
    WHERE ps.stock < %s AND ps.stock > 0
    ORDER BY ps.stock
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (threshold,))
            return cur.fetchall()

def get_out_of_stock():
    """Stokta olmayan ürünleri getir."""
    sql = """
    SELECT p.name, ps.size, ps.color
    FROM product_stock ps
    JOIN products p ON ps.product_id = p.id
    WHERE ps.stock = 0
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

def add_product(name, name_en, category_id, price, material, description, description_en):
    """Yeni ürün ekle."""
    sql = """
    INSERT INTO products (name, name_en, category_id, price, material, description, description_en)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (name, name_en, int(category_id), price, material, description, description_en))
            product_id = cur.fetchone()['id']
            conn.commit()
            return product_id

def update_product(product_id, name, name_en, category_id, price, material, description, description_en):
    """Ürün güncelle."""
    sql = """
    UPDATE products 
    SET name=%s, name_en=%s, category_id=%s, price=%s, material=%s, description=%s, description_en=%s
    WHERE id=%s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (name, name_en, int(category_id), price, material, description, description_en, product_id))
            conn.commit()

def delete_product(product_id):
    """Ürün sil."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM product_stock WHERE product_id = %s", (product_id,))
            cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
            conn.commit()

def add_stock(product_id, size, color, color_en, stock):
    """Stok ekle."""
    sql = """
    INSERT INTO product_stock (product_id, size, color, color_en, stock)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (product_id, size, color) 
    DO UPDATE SET stock = product_stock.stock + EXCLUDED.stock
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (product_id, size, color, color_en, stock))
            conn.commit()

def update_stock(stock_id, new_stock):
    """Stok güncelle."""
    sql = "UPDATE product_stock SET stock = %s WHERE id = %s"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (new_stock, stock_id))
            conn.commit()

def delete_stock(stock_id):
    """Stok sil."""
    sql = "DELETE FROM product_stock WHERE id = %s"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (stock_id,))
            conn.commit()

def add_category(name, name_en):
    """Kategori ekle."""
    sql = "INSERT INTO categories (name, name_en) VALUES (%s, %s) RETURNING id"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (name, name_en))
            cat_id = cur.fetchone()['id']
            conn.commit()
            return cat_id

def get_stats():
    """İstatistikleri getir."""
    stats = {}
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as count FROM products")
            stats['products'] = cur.fetchone()['count']
            
            cur.execute("SELECT COUNT(*) as count FROM categories")
            stats['categories'] = cur.fetchone()['count']
            
            cur.execute("SELECT COALESCE(SUM(stock), 0) as total FROM product_stock")
            stats['total_stock'] = cur.fetchone()['total']
            
            cur.execute("SELECT COUNT(*) as count FROM product_stock WHERE stock < 10 AND stock > 0")
            stats['low_stock'] = cur.fetchone()['count']
            
            cur.execute("SELECT COUNT(*) as count FROM product_stock WHERE stock = 0")
            stats['out_of_stock'] = cur.fetchone()['count']
    
    return stats


# Ana uygulama
if not check_password():
    st.stop()

# Header
st.markdown("""
<h1 style='text-align: center;'>⚙️ XStore Admin Paneli</h1>
""", unsafe_allow_html=True)

# Sidebar - Navigasyon
menu = st.sidebar.selectbox(
    "📌 Menü",
    ["📊 Dashboard", "📦 Ürünler", "📂 Kategoriler", "📈 Stok Yönetimi"]
)

# Çıkış butonu
if st.sidebar.button("🚪 Çıkış"):
    st.session_state.authenticated = False
    st.rerun()

# === DASHBOARD ===
if menu == "📊 Dashboard":
    st.header("📊 Genel Bakış")
    
    stats = get_stats()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📦 Toplam Ürün", stats['products'])
    with col2:
        st.metric("📂 Kategori", stats['categories'])
    with col3:
        st.metric("📊 Toplam Stok", stats['total_stock'])
    with col4:
        st.metric("⚠️ Düşük Stok", stats['low_stock'])
    with col5:
        st.metric("❌ Tükenen", stats['out_of_stock'])
    
    st.divider()
    
    # Düşük stok uyarıları
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚠️ Düşük Stok (< 10 adet)")
        low_stock = get_low_stock_products()
        if low_stock:
            for item in low_stock:
                st.write(f"• {item['name']} - {item['size']} {item['color']}: **{item['stock']} adet**")
        else:
            st.success("✅ Düşük stoklu ürün yok!")
    
    with col2:
        st.subheader("❌ Tükenen Ürünler")
        out_of_stock = get_out_of_stock()
        if out_of_stock:
            for item in out_of_stock:
                st.write(f"• {item['name']} - {item['size']} {item['color']}")
        else:
            st.success("✅ Tükenen ürün yok!")

# === ÜRÜNLER ===
elif menu == "📦 Ürünler":
    st.header("📦 Ürün Yönetimi")
    
    tab1, tab2, tab3 = st.tabs(["📋 Ürün Listesi", "➕ Yeni Ürün", "✏️ Düzenle/Sil"])
    
    # Ürün listesi
    with tab1:
        products = get_all_products()
        if products:
            st.table([{
                "ID": p['id'],
                "Ürün": p['name'],
                "Kategori": p['category'],
                "Fiyat": f"{p['price']}₺",
                "Malzeme": p['material'] or "-"
            } for p in products])
        else:
            st.info("Henüz ürün yok.")
    
    # Yeni ürün ekle
    with tab2:
        st.subheader("➕ Yeni Ürün Ekle")
        
        categories = get_all_categories()
        category_options = {row['name']: row['id'] for row in categories}
        
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Ürün Adı (TR)*")
                name_en = st.text_input("Ürün Adı (EN)")
                category = st.selectbox("Kategori*", options=list(category_options.keys()))
                price = st.number_input("Fiyat (₺)*", min_value=0.0, step=10.0)
            
            with col2:
                material = st.text_input("Malzeme")
                description = st.text_area("Açıklama (TR)")
                description_en = st.text_area("Açıklama (EN)")
            
            submit = st.form_submit_button("➕ Ürün Ekle", type="primary")
            
            if submit:
                if name and price > 0:
                    product_id = add_product(
                        name, name_en, category_options[category], 
                        price, material, description, description_en
                    )
                    st.success(f"✅ Ürün eklendi! (ID: {product_id})")
                    st.rerun()
                else:
                    st.error("❌ Ürün adı ve fiyat zorunludur!")
    
    # Düzenle/Sil
    with tab3:
        st.subheader("✏️ Ürün Düzenle / 🗑️ Sil")
        
        products = get_all_products()
        
        if products:
            product_options = {f"{p['id']} - {p['name']}": p for p in products}
            selected = st.selectbox("Ürün Seç", options=list(product_options.keys()))
            product = product_options[selected]
            
            categories = get_all_categories()
            category_options = {row['name']: row['id'] for row in categories}
            category_list = list(category_options.keys())
            
            with st.form("edit_product_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_name = st.text_input("Ürün Adı (TR)", value=product['name'])
                    new_name_en = st.text_input("Ürün Adı (EN)", value="")
                    
                    current_cat = product['category']
                    cat_index = category_list.index(current_cat) if current_cat in category_list else 0
                    new_category = st.selectbox("Kategori", options=category_list, index=cat_index)
                    
                    new_price = st.number_input("Fiyat (₺)", value=float(product['price']), min_value=0.0, step=10.0)
                
                with col2:
                    new_material = st.text_input("Malzeme", value=product['material'] or "")
                    new_description = st.text_area("Açıklama (TR)", value=product['description'] or "")
                    new_description_en = st.text_area("Açıklama (EN)", value="")
                
                col1, col2 = st.columns(2)
                with col1:
                    update_btn = st.form_submit_button("💾 Güncelle", type="primary")
                with col2:
                    delete_btn = st.form_submit_button("🗑️ Sil", type="secondary")
                
                if update_btn:
                    update_product(
                        product['id'], new_name, new_name_en, category_options[new_category],
                        new_price, new_material, new_description, new_description_en
                    )
                    st.success("✅ Ürün güncellendi!")
                    st.rerun()
                
                if delete_btn:
                    delete_product(product['id'])
                    st.success("✅ Ürün silindi!")
                    st.rerun()
        else:
            st.info("Henüz ürün yok.")

# === KATEGORİLER ===
elif menu == "📂 Kategoriler":
    st.header("📂 Kategori Yönetimi")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Mevcut Kategoriler")
        categories = get_all_categories()
        if categories:
            st.table([{
                "ID": c['id'],
                "Türkçe": c['name'],
                "İngilizce": c['name_en']
            } for c in categories])
        else:
            st.info("Henüz kategori yok.")
    
    with col2:
        st.subheader("➕ Yeni Kategori")
        with st.form("add_category_form"):
            cat_name = st.text_input("Kategori Adı (TR)*")
            cat_name_en = st.text_input("Kategori Adı (EN)*")
            
            if st.form_submit_button("➕ Ekle", type="primary"):
                if cat_name and cat_name_en:
                    cat_id = add_category(cat_name, cat_name_en)
                    st.success(f"✅ Kategori eklendi! (ID: {cat_id})")
                    st.rerun()
                else:
                    st.error("❌ Her iki alan da zorunludur!")

# === STOK YÖNETİMİ ===
elif menu == "📈 Stok Yönetimi":
    st.header("📈 Stok Yönetimi")
    
    products = get_all_products()
    
    if products:
        product_options = {f"{p['id']} - {p['name']}": p['id'] for p in products}
        selected = st.selectbox("📦 Ürün Seç", options=list(product_options.keys()))
        product_id = product_options[selected]
        
        tab1, tab2 = st.tabs(["📊 Mevcut Stok", "➕ Stok Ekle"])
        
        # Mevcut stok
        with tab1:
            stock_list = get_product_stock(product_id)
            
            if stock_list:
                st.subheader("📊 Stok Durumu")
                
                for row in stock_list:
                    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
                    
                    with col1:
                        st.text(f"📏 {row['size']}")
                    with col2:
                        st.text(f"🎨 {row['color']}")
                    with col3:
                        new_stock = st.number_input(
                            "Stok", 
                            value=int(row['stock']), 
                            min_value=0, 
                            key=f"stock_{row['id']}",
                            label_visibility="collapsed"
                        )
                    with col4:
                        if st.button("💾", key=f"save_{row['id']}"):
                            update_stock(row['id'], new_stock)
                            st.success("✅")
                            st.rerun()
                    with col5:
                        if st.button("🗑️", key=f"del_{row['id']}"):
                            delete_stock(row['id'])
                            st.rerun()
            else:
                st.info("ℹ️ Bu ürün için stok kaydı yok.")
        
        # Stok ekle
        with tab2:
            st.subheader("➕ Yeni Stok Ekle")
            
            with st.form("add_stock_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    size = st.selectbox("Beden", ["XS", "S", "M", "L", "XL", "XXL", "28", "30", "32", "34", "36", "38", "40", "42", "44"])
                    color = st.text_input("Renk (TR)*", placeholder="Siyah")
                
                with col2:
                    color_en = st.text_input("Renk (EN)", placeholder="Black")
                    stock = st.number_input("Adet*", min_value=1, value=10)
                
                if st.form_submit_button("➕ Stok Ekle", type="primary"):
                    if color:
                        add_stock(product_id, size, color, color_en or color, stock)
                        st.success(f"✅ {size} - {color}: {stock} adet eklendi!")
                        st.rerun()
                    else:
                        st.error("❌ Renk zorunludur!")
    else:
        st.info("Henüz ürün yok. Önce ürün ekleyin.")

# Footer
st.sidebar.divider()
st.sidebar.caption("XStore Admin v1.0")
