import redis
import sys
import time

print("==================== Redis 连接测试 ====================")
sys.stdout.flush() # 确保输出被刷新

# 假设 Redis 运行在 Docker 中，主机名为 'redis'
redis_host = 'redis'
redis_port = 6379

print(f"尝试连接到 Redis: {redis_host}:{redis_port}")
sys.stdout.flush()

try:
    print("创建连接...")
    sys.stdout.flush()
    
    # 尝试连接 Redis
    r = redis.Redis(
        host=redis_host,
        port=redis_port,
        socket_timeout=5,
        decode_responses=True
    )
    
    print("执行 PING...")
    sys.stdout.flush()
    
    # 测试连接
    result = r.ping()
    print(f"连接测试结果: {result}")
    sys.stdout.flush()
    
except Exception as e:
    print(f"连接错误: {type(e).__name__}: {e}")
    sys.stdout.flush()

# 尝试本地 localhost 连接
print("\n尝试连接到本地 Redis (localhost:6379)")
sys.stdout.flush()

try:
    r_local = redis.Redis(
        host="localhost",
        port=6379,
        socket_timeout=5,
        decode_responses=True
    )
    
    result_local = r_local.ping()
    print(f"本地连接测试结果: {result_local}")
    sys.stdout.flush()
    
except Exception as e:
    print(f"本地连接错误: {type(e).__name__}: {e}")
    sys.stdout.flush()

print("==================== 测试完成 ====================")
sys.stdout.flush() 