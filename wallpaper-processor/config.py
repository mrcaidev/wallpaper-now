import os
from dotenv import load_dotenv

# 加载当前目录下的 .env 文件
load_dotenv()

# Kafka Config
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "vectorizer-group")
WALLPAPER_SCRAPED_TOPIC = os.getenv("WALLPAPER_SCRAPED_TOPIC", "WallpaperScraped")
WALLPAPER_VECTORIZED_TOPIC = os.getenv("WALLPAPER_VECTORIZED_TOPIC", "WallpaperVectorized")

