# Use an official Python image
FROM python:3.11-slim

# Install system dependencies (git, nmap, etc. required by theHarvester)
RUN apt-get update && \
    apt-get install -y git nmap dnsutils && \
    rm -rf /var/lib/apt/lists/*

# Install theHarvester
RUN git clone https://github.com/laramies/theHarvester.git /opt/theHarvester && \
    sed -i 's/aiohttp==3.11.16/aiohttp==3.9.5/' /opt/theHarvester/requirements/base.txt && \
    pip install -r /opt/theHarvester/requirements/base.txt && \
    chmod +x /opt/theHarvester/theHarvester.py
ENV PATH="/opt/theHarvester:$PATH"

# Copy app code
WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Entrypoint (run FastAPI app with uvicorn)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
