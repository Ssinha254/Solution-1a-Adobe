FROM --platform=linux/amd64 python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "process_pdfs.py"]
