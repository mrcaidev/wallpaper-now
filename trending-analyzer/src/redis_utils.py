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
            redis_client = None # 确保失败时 client 为 None
            # raise # 可以在这里重新抛出，或者让调用者处理 None
        except Exception as e: # 捕获其他可能的初始化错误
             logger.error(f"初始化 Redis 客户端时发生未知错误: {e}")
             redis_client = None
    return redis_client  # 返回 Redis 客户端实例

def update_trending_wallpapers(batch_df):  # 定义更新趋势壁纸的函数，接收 Spark DataFrame
    """
    使用 RENAME 原子地刷新 Redis 中的趋势壁纸有序集合，
    使其精确匹配输入的 batch_df (应为最新窗口的数据).
    避免了短暂的空窗期。
    如果 batch_df 为空，则保留 Redis 中现有的数据。
    """
    r = get_redis_client()
    if not r:
        logger.error("Redis 客户端不可用，跳过 Redis 更新。")
        return

    try:
        trending_data = batch_df.rdd.map(lambda row: (row.wallpaper_id, row.score)).collect()
    except Exception as e:
        logger.error(f"从 Spark DataFrame 收集数据到 Driver 时出错: {e}", exc_info=True)
        return

    # 定义临时 key 和最终 key
    # 添加 App ID 保证在可能有多个 Spark 应用实例运行时临时 key 的唯一性
    temp_key = f"{config.REDIS_TRENDING_KEY}_temp" 
    final_key = config.REDIS_TRENDING_KEY

    # --- 修改后的逻辑 ---
    if not trending_data:
        # 如果最新窗口数据为空，保留 Redis 现有数据
        logger.info(f"最新窗口数据为空，保留 Redis key '{final_key}' 的现有数据。")
        return # 不执行任何 Redis 操作

    # 如果有数据，则执行原子刷新操作
    try:
        # 1. 将新数据写入临时 key
        members_scores = {str(item[0]): float(item[1]) for item in trending_data}
        # pipeline 保证写入和删除临时 key 的原子性（如果需要先删除）
        pipe = r.pipeline()
        pipe.delete(temp_key) # 先删除，确保 temp_key 是干净的
        pipe.zadd(temp_key, members_scores)
        results = pipe.execute() # results[0]是delete结果, results[1]是zadd结果

        # 检查 zadd 是否成功添加了数据
        # results[1] 是成功添加的新成员数量 (ZADD 返回值)
        if len(results) == 2 and results[1] is not None: # 确保 pipeline 执行成功且 ZADD 返回了值
            logger.debug(f"已将 {results[1]} 项写入临时 key: {temp_key}")

            # 2. 原子地将临时 key 重命名为最终 key
            # 使用 rename 而不是 RENAME NX，因为我们需要覆盖旧的 final_key
            rename_result = r.rename(temp_key, final_key)
            if rename_result: 
                 # RENAME 在 redis-py 3.x+ 成功时返回 True (早期版本可能不同)
                 logger.info(f"已原子刷新 Redis 有序集合 '{final_key}'，写入 {len(members_scores)} 项。")
            else:
                 # RENAME 失败比较罕见，除非源 key 不存在或目标 key 类型错误（理论上不会）
                 logger.error(f"原子重命名 key {temp_key} 到 {final_key} 失败。rename 返回: {rename_result}")
                 # 失败时临时 key 可能仍然存在，需要考虑是否手动删除
                 try:
                      if r.exists(temp_key):
                           r.delete(temp_key) # 尝试清理
                           logger.info(f"已清理重命名失败后残留的临时 key: {temp_key}")
                 except Exception as cleanup_e:
                      logger.error(f"清理重命名失败的临时 key {temp_key} 时出错: {cleanup_e}")

        else:
             # Pipeline 执行可能失败或 ZADD 未按预期工作
             logger.error(f"写入临时 key {temp_key} 的 pipeline 操作可能失败或 ZADD 未添加任何项。Pipeline 结果: {results}")
             # 尝试确保删除临时 key
             try:
                  if r.exists(temp_key):
                       r.delete(temp_key)
                       logger.info(f"已清理写入失败后残留的临时 key: {temp_key}")
             except Exception as cleanup_e:
                  logger.error(f"清理写入失败的临时 key {temp_key} 时出错: {cleanup_e}")

    except Exception as e:
        logger.error(f"使用 RENAME 刷新 Redis 时出错: {e}", exc_info=True)
        # 出错时尝试清理临时 key，避免残留
        try:
            # 检查 temp_key 是否还存在再删除
            if r.exists(temp_key):
                 r.delete(temp_key)
                 logger.info(f"已清理异常情况下残留的临时 key: {temp_key}")
        except Exception as cleanup_e:
            logger.error(f"清理异常情况下的临时 key {temp_key} 时出错: {cleanup_e}", exc_info=True)

# 在 Spark 中如何调用此函数的示例（使用 foreachBatch）
# streaming_query.writeStream \
#     .foreachBatch(lambda df, epoch_id: update_trending_wallpapers(df)) \
#     .start() 