# Build context is the repo root (one level above docker/).
# requirements.txt is installed at build time; bot/ code is volume-mounted at runtime.
FROM python:3.13-slim

WORKDIR /app

# Install dependencies into the image so they survive the volume mount
COPY bot/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

CMD ["python", "bot.py"]
