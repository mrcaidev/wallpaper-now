# config.py

# Kafka config
KAFKA_BOOTSTRAP_SERVERS = "localhost:29092"
KAFKA_GROUP_ID = "vectorizer-group"
WALLPAPER_SCRAPED_TOPIC = "WallpaperScraped"
WALLPAPER_VECTORIZED_TOPIC = "WallpaperVectorized"

# Model config
MODEL_PATH = "./models/bge"

# Optional logging config
ENABLE_LOGGING = True
LOG_LEVEL = "INFO"
