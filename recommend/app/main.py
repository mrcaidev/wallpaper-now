from fastapi import FastAPI
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# API路由
@app.get("/")
async def root():
    return {"message": "FastAPI服务正在运行"}