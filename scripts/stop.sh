#!/bin/bash

# 检查 PID 文件是否存在
if [ -f gunicorn.pid ]; then
  # 读取 PID
  PID=$(cat gunicorn.pid)

  # 停止进程
  kill $PID

  # 检查进程是否已成功停止
  if [ $? -eq 0 ]; then
    echo "Gunicorn (PID $PID) has been stopped."
    # 删除 PID 文件
    rm gunicorn.pid
  else
    echo "Failed to stop Gunicorn (PID $PID)."
  fi
else
  echo "PID file not found. Is Gunicorn running?"
fi
