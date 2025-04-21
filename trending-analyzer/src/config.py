import os  # 导入操作系统接口模块
from dotenv import load_dotenv  # 从 dotenv 库导入加载环境变量的函数

# 从 .env 文件加载环境变量
load_dotenv()  # 执行加载环境变量的操作

# Kafka 配置 - 使用 docker-compose 中的 brokers 地址
KAFKA_BROKERS = os.getenv('KAFKA_BROKERS', 'kafka-1:9092,kafka-2:9092,kafka-3:9092') # 获取 Kafka brokers 地址，提供默认值
# 默认 topic 基于 interaction-collector 可能的事件名称
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'interaction_collected') # 获取 Kafka topic 名称，提供默认值
KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'trending-analyzer-group') # 获取 Kafka 消费者组 ID，提供默认值

# Spark 配置
SPARK_MASTER = os.getenv('SPARK_MASTER', 'local[*]') # 获取 Spark Master URL，提供默认值 (local[*] 表示本地模式)
SPARK_APP_NAME = os.getenv('SPARK_APP_NAME', 'TrendingWallpaperAnalyzer') # 获取 Spark 应用名称，提供默认值
WINDOW_DURATION_SECONDS = int(os.getenv('WINDOW_DURATION_SECONDS', 3600)) # 获取窗口持续时间（秒），转为整数，提供默认值 (1 小时)
SLIDE_DURATION_SECONDS = int(os.getenv('SLIDE_DURATION_SECONDS', 600)) # 获取滑动间隔时间（秒），转为整数，提供默认值 (10 分钟)
TOP_N = int(os.getenv('TOP_N', 10)) # 获取要保留的热门壁纸数量，转为整数，提供默认值

# Redis 配置 - 需要外部提供，因为它不在 docker-compose 中
REDIS_HOST = os.getenv('REDIS_HOST') # 获取 Redis 主机地址，无默认值
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379)) # 获取 Redis 端口，转为整数，提供默认值
REDIS_DB = int(os.getenv('REDIS_DB', 0)) # 获取 Redis 数据库编号，转为整数，提供默认值
REDIS_TRENDING_KEY = os.getenv('REDIS_TRENDING_KEY', 'trending_wallpapers') # 获取 Redis 中存储趋势壁纸的键名，提供默认值

# 对必要的外部配置进行简单检查
if not REDIS_HOST: # 检查 REDIS_HOST 是否已提供
    raise ValueError("缺少必要的环境变量: REDIS_HOST") # 如果未提供，则抛出值错误异常 