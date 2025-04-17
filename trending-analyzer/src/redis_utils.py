import redis
import logging
from pyspark.sql import Row
from . import config

logger = logging.getLogger(__name__)

redis_client = None

def get_redis_client():
    """Initializes and returns a Redis client connection."""
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.StrictRedis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                db=config.REDIS_DB,
                decode_responses=True # 将响应解码为字符串
            )
            redis_client.ping() # 检查连接
            logger.info(f"成功连接到 Redis: {config.REDIS_HOST}:{config.REDIS_PORT}")
        except redis.exceptions.ConnectionError as e:
            logger.error(f"连接 Redis 失败: {e}")
            raise
    return redis_client

def update_trending_wallpapers(batch_df):
    """
    Updates the trending wallpapers sorted set in Redis based on the batch DataFrame.
    Assumes batch_df contains columns 'wallpaper_id' and 'score'.
    """
    try:
        r = get_redis_client()
        if not r:
            logger.error("Redis 客户端不可用，跳过更新。")
            return

        # 将 Spark DataFrame 行转换为 Redis ZADD 所需的字典
        # 将数据收集到 driver 节点 - 注意大型批次可能导致的内存问题
        trending_data = batch_df.rdd.map(lambda row: (row.wallpaper_id, row.score)).collect()

        if not trending_data:
            logger.info("此批次中没有需要更新到 Redis 的趋势数据。")
            return

        # 使用 pipeline 进行原子更新
        pipe = r.pipeline()
        # 在添加新数据前清除现有的有序集合
        pipe.delete(config.REDIS_TRENDING_KEY)
        # 使用 ZADD 添加新分数 {score1 member1 score2 member2 ...}
        # 注意：ZADD 期望 score 在前，member 在后
        members_scores = {item[0]: item[1] for item in trending_data}
        pipe.zadd(config.REDIS_TRENDING_KEY, members_scores)

        # 可选：如果有序集合变得过大，进行修剪（虽然排名已经做了这个限制，但可以保留以防万一）
        # pipe.zremrangebyrank(config.REDIS_TRENDING_KEY, 0, -config.TOP_N - 1)

        results = pipe.execute()
        logger.info(f"已更新 Redis 有序集合 '{config.REDIS_TRENDING_KEY}'，包含 {len(trending_data)} 项。Pipeline 结果: {results}")

    except Exception as e:
        logger.error(f"更新 Redis 时出错: {e}", exc_info=True)

# 在 Spark 中如何调用此函数的示例（使用 foreachBatch）
# streaming_query.writeStream \
#     .foreachBatch(lambda df, epoch_id: update_trending_wallpapers(df)) \
#     .start() 