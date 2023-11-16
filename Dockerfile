FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything
COPY . .

# Set executable permissions for stockfish
RUN chmod +x /app/bin/stockfish

CMD ["python3", "app.py"]
