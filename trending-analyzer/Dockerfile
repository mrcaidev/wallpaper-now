# 使用官方 Python 运行时作为父镜像
# 选择一个与 PySpark 和你的环境兼容的版本
FROM python:3.9-slim

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

# 将应用程序代码复制到容器中
COPY src/ /app/src/
# 复制 .env 文件 - 谨慎使用！推荐使用运行时环境变量。
# 如果取消注释此行，请确保在构建期间 .env 文件存在。
# COPY .env /app/.env

# 运行应用程序的命令
# 确保 Spark 环境（如 SPARK_HOME, Hadoop 配置）可用
# 这可能需要一个安装了 Spark 的自定义基础镜像，或者挂载 Spark 二进制文件
# 如果 Spark 在外部运行（例如集群），则可能只需要 PySpark 库
CMD ["python", "src/main.py"] 