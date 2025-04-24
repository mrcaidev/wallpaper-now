from fastapi import FastAPI
import logging
from app.kafka.UserCreatedComsumer import start_user_created_consumer, stop_user_created_consumer, get_user_created_consumer_status
from app.kafka.WallpaperCreatedComsumer import start_wallpaper_scraped_consumer, stop_wallpaper_scraped_consumer, get_wallpaper_scraped_consumer_status
from app.kafka.InteractionCollectedComsumer import start_interaction_collected_consumer,stop_interaction_collected_consumer
from app.service.recommendService import get_wallpaper_recommendations, get_random_wallpaper_recommend
import os
# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# 启动事件
@app.on_event("startup")
async def startup_event():
    await start_user_created_consumer()
    await start_wallpaper_scraped_consumer()
    await start_interaction_collected_consumer()
    logger.info("recommend service start, Kafka consumers start completely")

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    await stop_user_created_consumer()
    await stop_wallpaper_scraped_consumer()
    await stop_interaction_collected_consumer()
    logger.info("recommend service stop: Kafka consumers stop completely")

# API路由
@app.get("/")
async def root():
    return {"message": "FastAPI running..."}

# 用于检查Kafka消费者状态的端点
@app.get("/userCreateKafkaStatus")
async def kafka_status():
    return get_user_created_consumer_status()

@app.get("/wallpaperScrapedStatus")
async def wallpaper_kafka_status():
    return get_wallpaper_scraped_consumer_status()

@app.get("/recommendation/")
async def get_user_recommendation(user_id=None):
    if user_id is None or user_id == "":
        logger.info("Empty user_id, return random recommendation")
        return await get_random_wallpaper_recommend(10)
    else:
        logger.info("getUserRecommend: "+user_id)
        return await get_wallpaper_recommendations(user_id)