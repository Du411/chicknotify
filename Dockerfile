# FROM python:3.10-slim

# WORKDIR /app

# RUN apt-get update && apt-get install -y \
#     build-essential \
#     && rm -rf /var/lib/apt/lists/*

# COPY requirements.txt .

# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# RUN mkdir -p /app/logs

# RUN chmod +x start.sh

# ENV PYTHONPATH=/app

# ENV TZ=Asia/Taipei

# EXPOSE 8000

# CMD ["./start.sh"]



# -------- 建構階段 --------
FROM python:3.10-slim as builder

WORKDIR /tmp/build
    
# 複製依賴定義
COPY requirements.txt .
    
# 安裝建構依賴和 Python 依賴
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*
    
# -------- 執行階段 --------
FROM python:3.10-slim
    
WORKDIR /app
    
# 從建構階段複製已安裝的 Python 依賴
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
    
# 複製應用程式程式碼
COPY . .
    
RUN mkdir -p /app/logs
    
RUN chmod +x start.sh
    
ENV PYTHONPATH=/app
    
ENV TZ=Asia/Taipei
    
EXPOSE 80
    
CMD ["./start.sh"]