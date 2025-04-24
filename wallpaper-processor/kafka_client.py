# kafka_client.py
from kafka import KafkaConsumer, KafkaProducer
from config import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_GROUP_ID,
    WALLPAPER_SCRAPED_TOPIC,
)

import json

def init_consumer():
    return KafkaConsumer(
        WALLPAPER_SCRAPED_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=KAFKA_GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="latest",  # 只消费新消息
        enable_auto_commit=True,
    )

def init_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda m: json.dumps(m).encode("utf-8")
    )
