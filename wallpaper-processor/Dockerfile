# 使用官方轻量级 Python 镜像
FROM python:3.10-slim

# 设置工作目录（容器内）
WORKDIR /app

# 拷贝依赖文件并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝整个项目代码（包含 models, app, .py 文件）
COPY . .

# 设置默认启动命令：运行你的主入口 processor_entry.py
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
CMD ["python", "processor_entry.py"]
=======
CMD ["python", "processor_entry.py"]
>>>>>>> 304ca81 (Feat: Set up deployment)
=======
CMD ["python", "processor_entry.py"]
>>>>>>> 43fb737 (Feat: Add Dockerfile)
=======
CMD ["python", "processor_entry.py"]
>>>>>>> bee308a (Feat: Set up deployment)
=======
CMD ["python", "processor_entry.py"]
>>>>>>> 3fc4810 (Feat: Add Dockerfile)
