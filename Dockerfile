FROM python:3.11.4-alpine3.18
RUN apk update
RUN apk add gcc musl-dev mariadb-connector-c-dev
WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8080
COPY . .
CMD ["python", "app.py"]
