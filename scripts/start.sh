#!/bin/bash

# 激活虚拟环境
source .venv/bin/activate

# 启动 Gunicorn 并记录 PID
nohup gunicorn -w 2 -k uvicorn.workers.UvicornWorker --threads 4 app.main:app --bind 0.0.0.0:8080 > gunicorn.log 2>&1 &

# 获取 PID 并写入文件
echo $! > gunicorn.pid

echo "Gunicorn started with PID $(cat gunicorn.pid)"
