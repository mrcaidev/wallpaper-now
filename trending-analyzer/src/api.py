from fastapi import FastAPI, HTTPException, Query  # 导入 FastAPI 框架的核心类、HTTP 异常处理类和查询参数处理类
from fastapi.responses import JSONResponse  # 导入用于返回 JSON 响应的类 (虽然在此文件中未直接使用，但可能用于其他端点)
import redis  # 导入 Redis 客户端库
from typing import List  # 从 typing 模块导入 List 类型提示，用于定义响应模型
from . import config  # 从当前目录导入 config 模块，用于获取配置信息 (如 Redis 连接参数和 Key)

# 创建 FastAPI 应用实例
# title 参数设置了 API 文档中的标题
app = FastAPI(title="Trending Wallpaper API")

# 创建 Redis 客户端实例
# host: Redis 服务器地址，从 config 模块获取
# port: Redis 服务器端口，从 config 模块获取
# db: Redis 数据库编号，从 config 模块获取
# decode_responses=True: 将从 Redis 获取的响应 (通常是 bytes) 自动解码为字符串 (UTF-8)
redis_client = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, decode_responses=True)

# 定义一个 GET 请求的 API 端点
#路径为 "/api/v1/wallpapers/trending"
# response_model=List[str]: 指定响应体的数据结构是一个字符串列表 (即壁纸 ID 列表)
@app.get("/api/v1/wallpapers/trending", response_model=List[str])
# 定义处理该端点请求的异步函数 get_trending_wallpapers
# limit: 查询参数，限制返回的壁纸数量。使用 Query 进行参数校验和设置默认值
#   - default=10: 默认返回 10 个
#   - ge=0: 最小值必须大于等于 0
#   - le=100: 最大值必须小于等于 100
# offset: 查询参数，指定返回结果的偏移量 (用于分页)
#   - default=0: 默认从第 0 个开始
#   - ge=0: 最小值必须大于等于 0
async def get_trending_wallpapers(limit: int = Query(12, ge=0), offset: int = Query(0, ge=0)):
    """返回按权重排序且权重为正的壁纸ID列表"""  # 函数的文档字符串，会显示在 API 文档中
    try:  # 开始异常处理块，用于捕获 Redis 操作可能出现的错误
        if limit == 0:  # 检查 limit 参数是否为 0
            # 如果 limit 为 0，表示用户想要获取所有分数大于 0 的壁纸
            # 调用 redis_client 的 zrevrangebyscore 方法
            # config.REDIS_TRENDING_KEY: 要查询的 Redis 有序集合的 Key，从 config 模块获取
            # '+inf': 分数范围的最大值，表示正无穷大
            # '(0': 分数范围的最小值，表示大于 0 (开区间，不包含 0)
            wallpaper_ids = redis_client.zrevrangebyscore(
                config.REDIS_TRENDING_KEY, # 有序集合的键名
                '+inf',                 # 最大分数 (正无穷)
                '(0'                  # 最小分数 (大于 0)
            )
        else:  # 如果 limit 大于 0
            # 如果 limit 大于 0，表示用户想要获取指定数量的分数大于 0 的壁纸 (分页)
            # 调用 redis_client 的 zrevrangebyscore 方法，并使用 limit 和 offset 进行分页
            # config.REDIS_TRENDING_KEY: 要查询的 Redis 有序集合的 Key
            # '+inf': 分数范围的最大值 (正无穷)
            # '(0': 分数范围的最小值 (大于 0)
            # start=offset: 指定在分数范围内的结果中的偏移量 (从第 offset 个开始)
            # num=limit: 指定最多返回多少个结果
            wallpaper_ids = redis_client.zrevrangebyscore(
                config.REDIS_TRENDING_KEY, # 有序集合的键名
                '+inf',                 # 最大分数 (正无穷)
                '(0',                  # 最小分数 (大于 0)
                start=offset,          # 结果集的偏移量
                num=limit              # 返回的最大数量
            )
        return wallpaper_ids  # 返回获取到的壁纸 ID 列表
    except redis.exceptions.RedisError as e:  # 捕获 Redis 相关的错误
        # 如果发生 Redis 错误，记录错误并引发 HTTPException
        # status_code=500: 返回 HTTP 500 内部服务器错误状态码
        # detail=...: 返回具体的错误信息
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")