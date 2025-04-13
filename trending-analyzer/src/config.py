import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Kafka Configuration - Use brokers from docker-compose
KAFKA_BROKERS = os.getenv('KAFKA_BROKERS', 'kafka-1:9092,kafka-2:9092,kafka-3:9092')
# Default topic based on interaction-collector's likely event name
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'interaction_collected')
KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'trending-analyzer-group')

# Spark Configuration
SPARK_MASTER = os.getenv('SPARK_MASTER', 'local[*]') # Keep local default for easy testing
SPARK_APP_NAME = os.getenv('SPARK_APP_NAME', 'TrendingWallpaperAnalyzer')
WINDOW_DURATION_SECONDS = int(os.getenv('WINDOW_DURATION_SECONDS', 3600)) # 1 hour
SLIDE_DURATION_SECONDS = int(os.getenv('SLIDE_DURATION_SECONDS', 600)) # 10 minutes
TOP_N = int(os.getenv('TOP_N', 10))

# Redis Configuration - Needs to be provided externally as it's not in docker-compose
REDIS_HOST = os.getenv('REDIS_HOST') # No default, must be provided
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_TRENDING_KEY = os.getenv('REDIS_TRENDING_KEY', 'trending_wallpapers')

# Simple check for essential external config
if not REDIS_HOST:
    raise ValueError("Missing required environment variable: REDIS_HOST") 