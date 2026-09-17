FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY cascudo_core ./cascudo_core
COPY app ./app
RUN pip install --no-cache-dir -e .
EXPOSE 8000
CMD ["uvicorn","app.api.main:app","--host","0.0.0.0","--port","8000"]
