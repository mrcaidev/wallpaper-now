# 
FROM python:3.9-slim
# 
WORKDIR /code

# 安装必要系统工具和Java环境
RUN apt update && \  
    apt install -y openjdk-17-jdk && \  
    rm -rf /var/lib/apt/lists/*  

# 安装必要依赖
RUN pip install kafka-python

RUN pip install psycopg2-binary

RUN pip install fastapi

RUN pip install uvicorn

RUN pip install pyspark

RUN pip install aiokafka

RUN pip install numpy

RUN pip install dotenv
# 
COPY ./app /code/app

# 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7071"]