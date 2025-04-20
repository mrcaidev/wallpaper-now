import redis  # 导入 Redis 客户端库
import logging  # 导入日志模块
from pyspark.sql import Row  # 从 PySpark SQL 模块导入 Row 类型
from src import config  # 导入 config 模块

logger = logging.getLogger(__name__)  # 获取当前模块的 logger 实例

redis_client = None  # 初始化全局 Redis 客户端变量为 None

def get_redis_client():  # 定义获取 Redis 客户端的函数
    """Initializes and returns a Redis client connection."""  # 函数文档字符串
    global redis_client  # 声明使用全局变量 redis_client
    if redis_client is None:  # 检查 Redis 客户端是否尚未初始化
        try:  # 开始异常处理块
            redis_client = redis.StrictRedis(  # 创建 Redis 严格客户端实例
                host=config.REDIS_HOST,  # 设置 Redis 主机地址
                port=config.REDIS_PORT,  # 设置 Redis 端口
                db=config.REDIS_DB,  # 设置 Redis 数据库编号
                decode_responses=True # 将响应解码为字符串
            )
            redis_client.ping() # 检查连接，发送 PING 命令
            logger.info(f"成功连接到 Redis: {config.REDIS_HOST}:{config.REDIS_PORT}")
        except redis.exceptions.ConnectionError as e:  # 捕获连接错误
            logger.error(f"连接 Redis 失败: {e}")
            raise  # 重新抛出异常
    return redis_client  # 返回 Redis 客户端实例

def update_trending_wallpapers(batch_df):  # 定义更新趋势壁纸的函数，接收 Spark DataFrame
    """
    Updates the trending wallpapers sorted set in Redis based on the batch DataFrame.
    Stores all wallpapers without limiting to TOP_N.
    Assumes batch_df contains columns 'wallpaper_id' and 'score'.
    """  # 函数文档字符串
    try:  # 开始异常处理块
        r = get_redis_client()  # 获取 Redis 客户端
        if not r:  # 检查是否成功获取客户端
            logger.error("Redis 客户端不可用，跳过更新。")
            return  # 如果获取失败，则返回

        # 将 Spark DataFrame 行转换为 Redis ZADD 所需的字典
        trending_data = batch_df.rdd.map(lambda row: (row.wallpaper_id, row.score)).collect() # 转换 RDD 并收集结果到 Driver

        if not trending_data:  # 检查是否有趋势数据
            logger.info("此批次中没有需要更新到 Redis 的壁纸数据。")
            return  # 如果没有数据，则返回

        # 使用 pipeline 进行原子更新
        pipe = r.pipeline()  # 创建 Redis pipeline

        # 注意：我们不再删除现有数据，而是累积更新
        # 使用 ZADD 添加新分数，如果壁纸已存在则更新分数
        members_scores = {item[0]: item[1] for item in trending_data} # 将数据转换为 {member: score} 字典
        pipe.zadd(config.REDIS_TRENDING_KEY, members_scores) # 在 pipeline 中添加 ZADD 命令

        # 已经移除数量限制，所有壁纸数据都会保留

        results = pipe.execute() # 执行 pipeline 中的所有命令
        logger.info(f"已更新 Redis 有序集合 '{config.REDIS_TRENDING_KEY}'，包含 {len(trending_data)} 项。Pipeline 结果: {results}")

    except Exception as e:  # 捕获所有其他异常
        logger.error(f"更新 Redis 时出错: {e}", exc_info=True)

# 在 Spark 中如何调用此函数的示例（使用 foreachBatch）
# streaming_query.writeStream \
#     .foreachBatch(lambda df, epoch_id: update_trending_wallpapers(df)) \
#     .start() 