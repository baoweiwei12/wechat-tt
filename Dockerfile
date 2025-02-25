
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    pkg-config \
    libmariadb-dev \
    libmariadb-dev-compat \
    gcc \
    build-essential \
    python3-dev 

WORKDIR /serve-app

COPY ./requirements.txt /serve-app/requirements.txt

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r /serve-app/requirements.txt

COPY . /serve-app

EXPOSE 8000


CMD ["gunicorn", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "--threads", "4", "app.main:app", "--bind", "0.0.0.0:8000"]
