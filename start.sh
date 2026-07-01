#!/bin/bash
# Railway 启动脚本
set -e

echo "=== Railway 部署启动 ==="
echo "1. 安装依赖..."
pip install -r requirements.txt

echo "2. 收集静态文件..."
python manage.py collectstatic --noinput

echo "3. 数据库迁移..."
python manage.py migrate --noinput

echo "4. 启动 Gunicorn..."
gunicorn ai_qa_backend.wsgi \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
