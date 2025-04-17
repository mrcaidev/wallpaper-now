import os
from dotenv import load_dotenv

# 从 .env 文件加载环境变量
load_dotenv()

# Kafka 配置 - 使用 docker-compose 中的 brokers 地址
KAFKA_BROKERS = os.getenv('KAFKA_BROKERS', 'kafka-1:9092,kafka-2:9092,kafka-3:9092')
# 默认 topic 基于 interaction-collector 可能的事件名称
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'interaction_collected')
KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'trending-analyzer-group')

# Spark 配置
SPARK_MASTER = os.getenv('SPARK_MASTER', 'local[*]') # 保留 local[*] 作为默认值，方便测试
SPARK_APP_NAME = os.getenv('SPARK_APP_NAME', 'TrendingWallpaperAnalyzer')
WINDOW_DURATION_SECONDS = int(os.getenv('WINDOW_DURATION_SECONDS', 3600)) # 1 小时
SLIDE_DURATION_SECONDS = int(os.getenv('SLIDE_DURATION_SECONDS', 600)) # 10 分钟
TOP_N = int(os.getenv('TOP_N', 10))

# Redis 配置 - 需要外部提供，因为它不在 docker-compose 中
REDIS_HOST = os.getenv('REDIS_HOST') # 无默认值，必须提供
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_TRENDING_KEY = os.getenv('REDIS_TRENDING_KEY', 'trending_wallpapers')

# 对必要的外部配置进行简单检查
if not REDIS_HOST:
    raise ValueError("缺少必要的环境变量: REDIS_HOST") 