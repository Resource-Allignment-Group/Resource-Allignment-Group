FROM python:3.12
WORKDIR /backend
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p large_files_db/images large_files_db/reports
EXPOSE 5000
CMD ["python", "main.py"]
