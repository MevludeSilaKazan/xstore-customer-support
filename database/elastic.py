"""
XStore Elasticsearch Module
Akıllı ürün arama

Kurulum: pip install elasticsearch
"""

import os
from elasticsearch import Elasticsearch
from database.db import get_connection

# Elasticsearch bağlantısı - environment variable veya default
ES_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
es = Elasticsearch(ES_URL)

INDEX_NAME = "xstore_products"

def create_index():
    """Ürün index'i oluştur."""
    
    # Index ayarları - Türkçe için optimize
    settings = {
        "settings": {
            "analysis": {
                "char_filter": {
                    "turkish_char_filter": {
                        "type": "mapping",
                        "mappings": [
                            "ş => s", "Ş => S",
                            "ı => i", "İ => I", 
                            "ğ => g", "Ğ => G",
                            "ü => u", "Ü => U",
                            "ö => o", "Ö => O",
                            "ç => c", "Ç => C"
                        ]
                    }
                },
                "analyzer": {
                    "turkish_analyzer": {
                        "type": "custom",
                        "char_filter": ["turkish_char_filter"],
                        "tokenizer": "standard",
                        "filter": ["lowercase", "turkish_stemmer"]
                    },
                    "turkish_search": {
                        "type": "custom",
                        "char_filter": ["turkish_char_filter"],
                        "tokenizer": "standard",
                        "filter": ["lowercase"]
                    }
                },
                "filter": {
                    "turkish_stemmer": {
                        "type": "stemmer",
                        "language": "turkish"
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "name": {
                    "type": "text",
                    "analyzer": "turkish_analyzer",
                    "search_analyzer": "turkish_search",
                    "fields": {
                        "keyword": {"type": "keyword"}
                    }
                },
                "name_en": {
                    "type": "text",
                    "analyzer": "english"
                },
                "category": {
                    "type": "text",
                    "analyzer": "turkish_analyzer",
                    "search_analyzer": "turkish_search",
                    "fields": {
                        "keyword": {"type": "keyword"}
                    }
                },
                "category_en": {
                    "type": "text",
                    "analyzer": "english"
                },
                "description": {
                    "type": "text",
                    "analyzer": "turkish_analyzer",
                    "search_analyzer": "turkish_search"
                },
                "description_en": {
                    "type": "text",
                    "analyzer": "english"
                },
                "material": {
                    "type": "text"
                },
                "price": {
                    "type": "float"
                },
                "colors": {
                    "type": "text",
                    "analyzer": "turkish_analyzer",
                    "search_analyzer": "turkish_search",
                    "fields": {
                        "keyword": {"type": "keyword"}
                    }
                },
                "sizes": {
                    "type": "keyword"
                },
                "total_stock": {
                    "type": "integer"
                },
                "suggest": {
                    "type": "completion"
                }
            }
        }
    }
    
    # Varsa sil, yeniden oluştur
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
    
    es.indices.create(index=INDEX_NAME, body=settings)
    print(f"✅ Index '{INDEX_NAME}' oluşturuldu!")


def index_products():
    """PostgreSQL'den ürünleri al ve Elasticsearch'e yükle."""
    
    sql = """
    SELECT 
        p.id,
        p.name,
        p.name_en,
        c.name as category,
        c.name_en as category_en,
        p.description,
        p.description_en,
        p.material,
        p.price
    FROM products p
    JOIN categories c ON p.category_id = c.id
    """
    
    stock_sql = """
    SELECT size, color, color_en, stock
    FROM product_stock
    WHERE product_id = %s
    """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            products = cur.fetchall()
            
            for product in products:
                # Stok bilgilerini al
                cur.execute(stock_sql, (product['id'],))
                stocks = cur.fetchall()
                
                colors = list(set(s['color'] for s in stocks if s['stock'] > 0))
                colors_en = list(set(s['color_en'] for s in stocks if s['stock'] > 0))
                sizes = list(set(s['size'] for s in stocks if s['stock'] > 0))
                total_stock = sum(s['stock'] for s in stocks)
                
                # Elasticsearch document
                doc = {
                    "name": product['name'],
                    "name_en": product['name_en'] or product['name'],
                    "category": product['category'],
                    "category_en": product['category_en'],
                    "description": product['description'] or "",
                    "description_en": product['description_en'] or "",
                    "material": product['material'] or "",
                    "price": float(product['price']),
                    "colors": colors + colors_en,
                    "sizes": sizes,
                    "total_stock": total_stock,
                    "suggest": {
                        "input": [
                            product['name'],
                            product['name_en'] or "",
                            product['category'],
                            product['category_en']
                        ] + colors
                    }
                }
                
                # Index'e ekle
                es.index(index=INDEX_NAME, id=product['id'], document=doc)
            
            print(f"✅ {len(products)} ürün index'lendi!")


def search_products(query: str, size: str = None, color: str = None, max_results: int = 5):
    """
    Akıllı ürün arama.
    
    Args:
        query: Arama terimi
        size: Beden filtresi (opsiyonel)
        color: Renk filtresi (opsiyonel)
        max_results: Maksimum sonuç sayısı
    
    Returns:
        Ürün listesi
    """
    
    # Multi-match query - birden fazla alanda ara
    must_queries = [
        {
            "multi_match": {
                "query": query,
                "fields": [
                    "name^3",        # İsim en önemli (3x boost)
                    "name_en^3",
                    "category^2",    # Kategori (2x boost)
                    "category_en^2",
                    "description",
                    "description_en",
                    "material",
                    "colors"
                ],
                "type": "best_fields",
                "fuzziness": "AUTO"  # Yazım hatalarını tolere et
            }
        }
    ]
    
    # Filtreler
    filter_queries = []
    
    if size:
        filter_queries.append({"term": {"sizes": size.upper()}})
    
    if color:
        filter_queries.append({
            "bool": {
                "should": [
                    {"wildcard": {"colors": f"*{color.lower()}*"}},
                    {"match": {"colors": color}}
                ]
            }
        })
    
    # Stokta olan ürünleri önceliklendir
    should_queries = [
        {"range": {"total_stock": {"gt": 0, "boost": 2}}}
    ]
    
    # Query oluştur
    search_query = {
        "query": {
            "bool": {
                "must": must_queries,
                "filter": filter_queries,
                "should": should_queries
            }
        },
        "size": max_results,
        "sort": [
            "_score",
            {"total_stock": "desc"}
        ]
    }
    
    # Ara
    response = es.search(index=INDEX_NAME, body=search_query)
    
    # Sonuçları formatla
    results = []
    for hit in response['hits']['hits']:
        source = hit['_source']
        results.append({
            "id": hit['_id'],
            "name": source['name'],
            "category": source['category'],
            "price": source['price'],
            "description": source.get('description', ''),
            "material": source.get('material', ''),
            "colors": source.get('colors', []),
            "sizes": source.get('sizes', []),
            "total_stock": source.get('total_stock', 0),
            "score": hit['_score']
        })
    
    return results


def suggest_products(query: str, max_results: int = 5):
    """
    Otomatik tamamlama önerileri.
    
    Args:
        query: Kullanıcının yazdığı
        max_results: Maksimum öneri sayısı
    
    Returns:
        Öneri listesi
    """
    
    suggest_query = {
        "suggest": {
            "product-suggest": {
                "prefix": query,
                "completion": {
                    "field": "suggest",
                    "size": max_results,
                    "fuzzy": {
                        "fuzziness": "AUTO"
                    }
                }
            }
        }
    }
    
    response = es.search(index=INDEX_NAME, body=suggest_query)
    
    suggestions = []
    for option in response['suggest']['product-suggest'][0]['options']:
        suggestions.append({
            "text": option['text'],
            "id": option['_id'],
            "score": option['_score']
        })
    
    return suggestions


def check_connection():
    """Elasticsearch bağlantısını kontrol et."""
    try:
        info = es.info()
        return True, info['version']['number']
    except Exception as e:
        return False, str(e)


# Test
if __name__ == "__main__":
    print("🔍 Elasticsearch XStore Module")
    print("=" * 50)
    
    # Bağlantı kontrolü
    connected, version = check_connection()
    if connected:
        print(f"✅ Elasticsearch bağlantısı OK (v{version})")
    else:
        print(f"❌ Bağlantı hatası: {version}")
        exit(1)
    
    # Index oluştur
    print("\n📦 Index oluşturuluyor...")
    create_index()
    
    # Ürünleri index'le
    print("\n📥 Ürünler index'leniyor...")
    index_products()
    
    # Test aramaları
    print("\n🔍 Test aramaları:")
    print("-" * 50)
    
    test_queries = [
        "siyah tişört",
        "tisort",  # Yazım hatası
        "sweatshirt M beden",
        "mont",
        "black t-shirt"
    ]
    
    for q in test_queries:
        print(f"\n🔎 Arama: '{q}'")
        results = search_products(q)
        if results:
            for r in results[:3]:
                stock_status = "✅" if r['total_stock'] > 0 else "❌"
                print(f"   {stock_status} {r['name']} - {r['price']}₺ (skor: {r['score']:.2f})")
        else:
            print("   Sonuç bulunamadı")
