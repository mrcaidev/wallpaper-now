from concurrent.futures import ThreadPoolExecutor
from kafka_client import init_consumer, init_producer
from config import WALLPAPER_VECTORIZED_TOPIC, KAFKA_GROUP_ID, WALLPAPER_SCRAPED_TOPIC
from processor_logic import process_wallpaper
import os
from app.utils.logger import get_logger
import socket

logger = get_logger(__name__)

CONSUMER_NAME = os.getenv("CONSUMER_NAME") or socket.gethostname()

producer = init_producer()

# $env:CONSUMER_NAME = "consumer-1"
# python processor_entry.py

def consume_partition():
    consumer = init_consumer()

    consumer.subscribe([WALLPAPER_SCRAPED_TOPIC])

    logger.info(f"✅ {CONSUMER_NAME} 加入 group：{KAFKA_GROUP_ID}，等待 Kafka 分配分区...")

    for msg in consumer:
        logger.info(f"{CONSUMER_NAME} 收到 📥 来自 partition {msg.partition} 的消息：{msg.value}")
        
        processed = process_wallpaper(msg.value)

        # 模拟处理后发回另一个 Kafka topic
        producer.send(WALLPAPER_VECTORIZED_TOPIC, processed)
        logger.info(f"{CONSUMER_NAME} 📤 Partition {msg.partition} 处理完成并返回")


if __name__ == "__main__":
    consume_partition()