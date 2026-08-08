FROM python:3.11-slim

# ============================================================
# INSTALLA TUTTE LE DIPENDENZE DI SISTEMA PER PLAYWRIGHT
# ============================================================
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libnspr4 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libxkbcommon0 \
    && rm -rf /var/lib/apt/lists/*

# ============================================================
# INSTALLA PLAYWRIGHT
# ============================================================
RUN pip install --upgrade pip && \
    pip install playwright

RUN playwright install chromium

# ============================================================
# COPIA IL BOT
# ============================================================
WORKDIR /app
COPY bot_multi_stealth.py .

# ============================================================
# COMANDO DI AVVIO
# ============================================================
CMD ["python", "-u", "bot_multi_stealth.py"]