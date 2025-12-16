FROM python:3.9-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY *.py ./

# 设置 Python 环境变量
ENV PYTHONUNBUFFERED=1

# 默认命令
CMD ["python", "main.py"]
