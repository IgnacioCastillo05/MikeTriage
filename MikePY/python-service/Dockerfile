FROM python:3.11-slim

RUN pip install fastapi uvicorn

COPY app/ /app/

WORKDIR /app

EXPOSE 8087

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8085"]