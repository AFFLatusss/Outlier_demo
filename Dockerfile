# Use official Python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app



# Install only minimal system dependencies needed for pymssql
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        freetds-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout=180 -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt

# Copy app code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Streamlit environment variables
ENV STREAMLIT_SERVER_ENABLECORS=false
ENV STREAMLIT_SERVER_ENABLEXSFRPROTECTION=false
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_PORT=8501

# Run the Streamlit app
CMD ["streamlit", "run", "main.py"]
