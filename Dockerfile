FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=120 \
    PYTHONPATH=/workspace \
    HF_HOME=/root/.cache/huggingface

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install CPU-only PyTorch to avoid downloading CUDA packages
RUN pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    torch==2.5.1

# Install compatible scientific and NLP dependencies
RUN pip install --no-cache-dir \
    numpy==1.26.4 \
    scipy==1.12.0 \
    pandas==2.2.3 \
    pyarrow==16.1.0 \
    transformers==4.44.2 \
    huggingface-hub==0.25.2

# Install the remaining project dependencies
RUN pip install --no-cache-dir \
    --prefer-binary \
    --retries 5 \
    -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "app/main.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]