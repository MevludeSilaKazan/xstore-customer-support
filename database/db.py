"""
XStore Database Module
PostgreSQL bağlantısı ve ürün sorguları
"""

import os
from typing import List, Dict, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    """Veritabanı bağlantısı oluştur."""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def search_products(query: str, lang: str = "tr") -> List[Dict]:
    """
    Ürün ara (isim veya açıklamada).
    
    Args:
        query: Arama terimi
        lang: Dil (tr/en)
    
    Returns:
        Ürün listesi
    """
    name_col = "p.name" if lang == "tr" else "COALESCE(p.name_en, p.name)"
    desc_col = "p.description" if lang == "tr" else "COALESCE(p.description_en, p.description)"
    cat_col = "c.name" if lang == "tr" else "c.name_en"
    
    sql = f"""
    SELECT 
        p.id,
        {name_col} as name,
        {cat_col} as category,
        p.price,
        {desc_col} as description,
        p.material
    FROM products p
    JOIN categories c ON p.category_id = c.id
    WHERE 
        LOWER(p.name) LIKE LOWER(%s) OR 
        LOWER(p.name_en) LIKE LOWER(%s) OR
        LOWER(p.description) LIKE LOWER(%s) OR
        LOWER(c.name) LIKE LOWER(%s) OR
        LOWER(c.name_en) LIKE LOWER(%s)
    LIMIT 10
    """
    
    search_term = f"%{query}%"
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (search_term, search_term, search_term, search_term, search_term))
            return cur.fetchall()


def get_product_by_id(product_id: int, lang: str = "tr") -> Optional[Dict]:
    """Ürün detayını getir."""
    name_col = "p.name" if lang == "tr" else "COALESCE(p.name_en, p.name)"
    desc_col = "p.description" if lang == "tr" else "COALESCE(p.description_en, p.description)"
    cat_col = "c.name" if lang == "tr" else "c.name_en"
    
    sql = f"""
    SELECT 
        p.id,
        {name_col} as name,
        {cat_col} as category,
        p.price,
        {desc_col} as description,
        p.material
    FROM products p
    JOIN categories c ON p.category_id = c.id
    WHERE p.id = %s
    """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (product_id,))
            return cur.fetchone()


def get_product_stock(product_id: int, lang: str = "tr") -> List[Dict]:
    """Ürünün stok durumunu getir."""
    color_col = "color" if lang == "tr" else "COALESCE(color_en, color)"
    
    sql = f"""
    SELECT 
        size,
        {color_col} as color,
        stock
    FROM product_stock
    WHERE product_id = %s
    ORDER BY 
        CASE size 
            WHEN 'XS' THEN 1 
            WHEN 'S' THEN 2 
            WHEN 'M' THEN 3 
            WHEN 'L' THEN 4 
            WHEN 'XL' THEN 5
            WHEN 'XXL' THEN 6
            ELSE 7
        END,
        color
    """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (product_id,))
            return cur.fetchall()


def check_stock(product_name: str, size: str = None, color: str = None) -> Dict:
    """
    Belirli ürün/beden/renk için stok kontrolü.
    
    Returns:
        {
            "product": {...},
            "stock_info": [...],
            "available": True/False,
            "total_stock": int
        }
    """
    # Önce ürünü bul
    products = search_products(product_name)
    
    if not products:
        return {"available": False, "message": "Ürün bulunamadı"}
    
    product = products[0]  # En alakalı ürün
    stock_list = get_product_stock(product["id"])
    
    # Filtrele
    filtered_stock = stock_list
    if size:
        filtered_stock = [s for s in filtered_stock if s["size"].upper() == size.upper()]
    if color:
        filtered_stock = [s for s in filtered_stock if color.lower() in s["color"].lower()]
    
    total = sum(s["stock"] for s in filtered_stock)
    
    return {
        "product": product,
        "stock_info": filtered_stock,
        "available": total > 0,
        "total_stock": total
    }


def get_products_by_category(category: str, lang: str = "tr") -> List[Dict]:
    """Kategoriye göre ürünleri getir."""
    name_col = "p.name" if lang == "tr" else "COALESCE(p.name_en, p.name)"
    cat_col = "c.name" if lang == "tr" else "c.name_en"
    
    sql = f"""
    SELECT 
        p.id,
        {name_col} as name,
        {cat_col} as category,
        p.price,
        p.material
    FROM products p
    JOIN categories c ON p.category_id = c.id
    WHERE LOWER(c.name) LIKE LOWER(%s) OR LOWER(c.name_en) LIKE LOWER(%s)
    ORDER BY p.price
    """
    
    search_term = f"%{category}%"
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (search_term, search_term))
            return cur.fetchall()


def get_all_categories(lang: str = "tr") -> List[Dict]:
    """Tüm kategorileri getir."""
    name_col = "name" if lang == "tr" else "name_en"
    
    sql = f"SELECT id, {name_col} as name FROM categories ORDER BY id"
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()


def get_price_range(min_price: float = None, max_price: float = None, lang: str = "tr") -> List[Dict]:
    """Fiyat aralığına göre ürün getir."""
    name_col = "p.name" if lang == "tr" else "COALESCE(p.name_en, p.name)"
    cat_col = "c.name" if lang == "tr" else "c.name_en"
    
    conditions = []
    params = []
    
    if min_price is not None:
        conditions.append("p.price >= %s")
        params.append(min_price)
    if max_price is not None:
        conditions.append("p.price <= %s")
        params.append(max_price)
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    sql = f"""
    SELECT 
        p.id,
        {name_col} as name,
        {cat_col} as category,
        p.price
    FROM products p
    JOIN categories c ON p.category_id = c.id
    WHERE {where_clause}
    ORDER BY p.price
    LIMIT 20
    """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def format_product_info(product: Dict, stock_info: List[Dict] = None, lang: str = "tr") -> str:
    """Ürün bilgisini okunabilir formatta döndür."""
    if lang == "tr":
        text = f"""
📦 **{product['name']}**
   Kategori: {product['category']}
   Fiyat: {product['price']}₺
   Malzeme: {product.get('material', 'Belirtilmemiş')}
"""
        if product.get('description'):
            text += f"   Açıklama: {product['description']}\n"
        
        if stock_info:
            text += "\n   📊 Stok Durumu:\n"
            for s in stock_info:
                status = "✅" if s['stock'] > 0 else "❌"
                text += f"   {status} {s['size']} - {s['color']}: {s['stock']} adet\n"
    else:
        text = f"""
📦 **{product['name']}**
   Category: {product['category']}
   Price: {product['price']}₺
   Material: {product.get('material', 'Not specified')}
"""
        if product.get('description'):
            text += f"   Description: {product['description']}\n"
        
        if stock_info:
            text += "\n   📊 Stock Status:\n"
            for s in stock_info:
                status = "✅" if s['stock'] > 0 else "❌"
                text += f"   {status} {s['size']} - {s['color']}: {s['stock']} pcs\n"
    
    return text


# Test
if __name__ == "__main__":
    print("🔍 Testing database connection...\n")
    
    # Kategorileri listele
    print("📂 Kategoriler:")
    for cat in get_all_categories():
        print(f"  - {cat['name']}")
    
    print("\n🔍 'tişört' araması:")
    for p in search_products("tişört"):
        print(f"  - {p['name']} - {p['price']}₺")
    
    print("\n📦 Stok kontrolü (Oversize Tişört, M beden):")
    result = check_stock("oversize tişört", size="M")
    if result.get("product"):
        print(format_product_info(result["product"], result["stock_info"]))
