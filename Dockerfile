FROM --platform=linux/amd64 python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && python -m spacy download en_core_web_sm

COPY . .

# Disable pip's cache and prevent internet access after build
RUN rm -rf ~/.cache/pip

CMD ["python", "process_pdfs.py"]
