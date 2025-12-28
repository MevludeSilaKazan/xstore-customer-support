# Python 3.11 slim image
FROM python:3.11-slim

# Çalışma dizini
WORKDIR /app

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıkları
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyaları
COPY . .

# Streamlit ayarları
RUN mkdir -p ~/.streamlit
RUN echo "\
[server]\n\
headless = true\n\
enableCORS = false\n\
enableXsrfProtection = false\n\
\n\
[theme]\n\
primaryColor = '#667eea'\n\
backgroundColor = '#f5f5f5'\n\
secondaryBackgroundColor = '#ffffff'\n\
textColor = '#333333'\n\
" > ~/.streamlit/config.toml

# Port
EXPOSE 8501 8502

# Default komut
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
