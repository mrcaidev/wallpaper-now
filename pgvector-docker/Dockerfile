# 使用官方PostgreSQL镜像
FROM postgres:15

# 安装编译pgvector所需的依赖
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    git \
    postgresql-server-dev-15

# 下载并编译安装pgvector
RUN git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git && \
    cd pgvector && \
    make && \
    make install && \
    cd .. && \
    rm -rf pgvector

# 将初始化脚本复制到容器中
COPY docker-entrypoint-initdb.d/init.sql /docker-entrypoint-initdb.d/
