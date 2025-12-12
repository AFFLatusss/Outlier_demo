# Use full Debian-based Python image
FROM python:3.11

# Set working directory
WORKDIR /app

# Install system dependencies for pymssql
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    freetds-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout=180 -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt

# Copy project files
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_ENABLECORS=false
ENV STREAMLIT_SERVER_ENABLEXSFRPROTECTION=false
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_PORT=8501

# Run Streamlit app
CMD ["streamlit", "run", "main.py"]
