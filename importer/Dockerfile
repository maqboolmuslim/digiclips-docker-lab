FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# do not run as root (client rule)
RUN useradd --create-home appuser
USER appuser
CMD ["python", "import_captions.py"]
