# 使用官方 Python 运行时作为父镜像
# 选择一个与 PySpark 和你的环境兼容的版本
FROM python:3.9-slim

# 安装Java和必要工具
RUN apt-get update && \
    apt-get install -y procps default-jdk wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 设置Java环境变量
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH=$PATH:$JAVA_HOME/bin

# 设置 Python 环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 设置容器内的工作目录
WORKDIR /app

# 安装 PySpark 或其他库可能需要的系统依赖项
# (可选，取决于你的基础镜像和具体需求)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# 安装所需的 Python 包
# 首先只复制 requirements 文件以利用 Docker 缓存
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 确保安装了FastAPI和uvicorn
RUN pip install --no-cache-dir fastapi uvicorn

# 将应用程序代码复制到容器中
COPY src/ /app/src/

# 下载Kafka连接器
RUN python -m src.download_kafka_jar

# 创建启动脚本
RUN echo '#!/bin/bash\n\
# 启动API服务\n\
uvicorn src.api:app --host 0.0.0.0 --port 8000 &\n\
\n\
# 启动主应用程序\n\
python -m src.main\n' > /app/start.sh && \
    chmod +x /app/start.sh

# 暴露API端口
EXPOSE 8000

# 运行启动脚本
CMD ["/app/start.sh"] 