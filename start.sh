#!/bin/bash
# XStore Docker Başlatma Scripti

echo "🐳 XStore Docker Başlatılıyor..."
echo "================================"

# .env dosyası kontrolü
if [ ! -f .env ]; then
    echo "❌ .env dosyası bulunamadı!"
    echo "📝 .env.example dosyasını .env olarak kopyalayın ve düzenleyin:"
    echo "   cp .env.example .env"
    exit 1
fi

# Docker Compose başlat
echo "📦 Container'lar başlatılıyor..."
docker-compose up -d

# Elasticsearch'ün hazır olmasını bekle
echo "⏳ Elasticsearch hazırlanıyor..."
sleep 10

# Elasticsearch'ün tamamen çalıştığını kontrol et
until curl -s http://localhost:9200 > /dev/null; do
    echo "   Bekleniyor..."
    sleep 5
done
echo "✅ Elasticsearch hazır!"

# Index oluştur ve ürünleri yükle
echo "📥 Ürünler index'leniyor..."
docker-compose exec -T app python -m database.elastic

echo ""
echo "🎉 XStore hazır!"
echo "================================"
echo "🛒 Müşteri Chatbot: http://localhost:8501"
echo "⚙️  Admin Paneli:   http://localhost:8502"
echo "🔍 Elasticsearch:   http://localhost:9200"
echo ""
echo "📌 Durdur: docker-compose down"
echo "📌 Loglar: docker-compose logs -f"
