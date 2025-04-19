from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import redis
from typing import List
from . import config

app = FastAPI(title="Trending Wallpaper API")

# 复用 redis_utils 的连接逻辑
redis_client = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, decode_responses=True)

@app.get("/api/v1/wallpapers/trending")
async def get_trending_wallpapers(limit: int = Query(10, ge=1, le=100), offset: int = Query(0, ge=0)):
    """返回按权重排序的壁纸ID集合"""
    try:
        start = offset
        end = offset + limit - 1
        # ZREVRANGE 返回降序排列 items
        ids_scores = redis_client.zrevrange(config.REDIS_TRENDING_KEY, start, end, withscores=True)
        data = [
            {"wallpaper_id": wid, "score": score, "rank": idx + 1 + offset}
            for idx, (wid, score) in enumerate(ids_scores)
        ]
        return JSONResponse(status_code=200, content={"data": data, "limit": limit, "offset": offset})
    except redis.exceptions.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}") 