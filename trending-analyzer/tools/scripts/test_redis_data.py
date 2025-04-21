#!/usr/bin/env python
"""
向Redis添加测试数据并验证
"""
import redis
import os
from dotenv import load_dotenv
import time

# 加载环境变量
load_dotenv()

# 从环境变量获取Redis配置
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_db = int(os.getenv("REDIS_DB", 0))
redis_key = os.getenv("REDIS_TRENDING_KEY", "trending_wallpapers")

print(f"连接到Redis: {redis_host}:{redis_port} (DB: {redis_db})")

try:
    # 连接Redis
    r = redis.StrictRedis(
        host=redis_host,
        port=redis_port,
        db=redis_db,
        decode_responses=True
    )
    
    # 添加一些测试数据
    print(f"\n向 '{redis_key}' 添加测试数据...")
    
    # 清空现有数据
    r.delete(redis_key)
    
    # 添加模拟壁纸数据（ID和分数）
    test_data = [
        ("wallpaper1001", 120.5),
        ("wallpaper1002", 85.3),
        ("wallpaper1003", 192.1),
        ("wallpaper1004", 65.7),
        ("wallpaper1005", 210.9)
    ]
    
    for wallpaper_id, score in test_data:
        r.zadd(redis_key, {wallpaper_id: score})
        print(f"  已添加: {wallpaper_id}, 分数: {score}")
    
    time.sleep(1)  # 稍等一会
    
    # 验证数据
    print("\n验证数据:")
    total = r.zcard(redis_key)
    print(f"'{redis_key}' 中共有 {total} 个项目")
    
    # 获取所有壁纸并按分数降序排列
    all_wallpapers = r.zrevrange(redis_key, 0, -1, withscores=True)
    
    print("\n按排名顺序的壁纸:")
    for i, (wallpaper_id, score) in enumerate(all_wallpapers):
        print(f"  {i+1}. ID: {wallpaper_id}, 分数: {score}")
    
    print("\n✅ 测试数据已成功添加到Redis")
    
except Exception as e:
    print(f"❌ 错误: {e}") 