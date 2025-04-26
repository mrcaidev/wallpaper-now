import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer
from app.service.recommendService import update_user_profile
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kafka配置
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BROKERS")
KAFKA_TOPIC = "InteractionCollected"

# 全局变量存储消费者实例和消费任务
consumer_task = None

# 处理用户创建消息的函数
async def process_interaction_collected_message(user_data):
    logger.info(f"processing interaction: {user_data}")
    await update_user_profile(user_data['userId'], user_data['wallpaperId'], user_data['weight'])

# Kafka消费者协程
async def consume():
    """持续消费Kafka消息的协程"""
    try:
        # 创建消费者
        consumer = AIOKafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            enable_auto_commit=True,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        # 启动消费者
        await consumer.start()
        logger.info(f"Begin consuming Kafka Topic: {KAFKA_TOPIC}")
        
        # 持续消费消息
        async for msg in consumer:
            logger.info(f"event accepted: {msg.topic}, {msg.partition}, {msg.offset}")
            try:
                await process_interaction_collected_message(msg.value)
            except Exception as e:
                logger.error(f"error detail: {str(e)}", exc_info=True)
                continue  # 显式继续下一条消息
    except Exception as e:
        logger.error(f"Kafka consume error: {e}")

# 启动消费者
async def start_interaction_collected_consumer():
    """启动Kafka消费任务"""
    global consumer_task
    loop = asyncio.get_event_loop()
    consumer_task = loop.create_task(consume())
    logger.info(KAFKA_TOPIC + " Kafka consumer started")
    return consumer_task

# 停止消费者
async def stop_interaction_collected_consumer():
    """停止Kafka消费任务"""
    global consumer_task
    if consumer_task:
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            logger.info(KAFKA_TOPIC + "Kafka consumer stopped")
        consumer_task = None

# 检查消费者状态
def get_interaction_collected_consumer_status():
    """获取Kafka消费者状态"""
    if consumer_task and not consumer_task.done():
        return {"status": "running"}
    return {"status": "stopped"}