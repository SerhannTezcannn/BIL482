FROM python:3.10-slim

WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose API port
EXPOSE 8080

# Run the API from the code directory
WORKDIR /app/code
CMD ["python", "api.py"]
