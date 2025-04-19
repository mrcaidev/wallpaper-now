#!/usr/bin/env python
"""
Kafka 模拟数据生成器 - 用于生成高频率、大数据量的用户互动数据发送到 Kafka
"""
import json
import random
import threading
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv
from kafka import KafkaProducer
from kafka.errors import KafkaError
import os
import argparse

# 加载环境变量
load_dotenv()

# Kafka 配置
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "interaction_collected")

# 模拟数据配置
DEFAULT_TOTAL_USERS = 1000      # 模拟用户数量
DEFAULT_TOTAL_WALLPAPERS = 500  # 模拟壁纸数量
DEFAULT_THREADS = 5             # 生产者线程数
DEFAULT_BATCH_SIZE = 100        # 每批次消息数
DEFAULT_INTERVAL = 0.1          # 每批次间隔(秒)

# 互动权重值分布 - 根据不同类型互动有不同的权重
INTERACTION_WEIGHTS = [
    (1.0, 0.45),    # 浏览，权重1.0，45%概率
    (2.0, 0.25),    # 点赞，权重2.0，25%概率
    (5.0, 0.15),    # 下载，权重5.0，15%概率
    (7.0, 0.08),    # 收藏，权重7.0，8%概率
    (10.0, 0.05),   # 设为背景，权重10.0，5%概率
    (-0.5, 0.02)    # 取消点赞/收藏，负权重-0.5，2%概率
]

# 热门壁纸列表 - 这些壁纸会更频繁地被互动
HOT_WALLPAPERS_PERCENTAGE = 0.05  # 热门壁纸比例
HOT_WALLPAPER_FACTOR = 5         # 热门壁纸被选中的几率提升倍数

# 活跃用户列表 - 这些用户会更频繁地产生互动
ACTIVE_USERS_PERCENTAGE = 0.1    # 活跃用户比例
ACTIVE_USER_FACTOR = 3           # 活跃用户被选中的几率提升倍数

class KafkaStubGenerator:
    """Kafka消息生成器，模拟用户与壁纸的互动行为"""
    
    def __init__(
        self,
        total_users: int = DEFAULT_TOTAL_USERS,
        total_wallpapers: int = DEFAULT_TOTAL_WALLPAPERS,
        threads: int = DEFAULT_THREADS,
        batch_size: int = DEFAULT_BATCH_SIZE,
        interval: float = DEFAULT_INTERVAL
    ):
        """初始化生成器配置"""
        self.total_users = total_users
        self.total_wallpapers = total_wallpapers
        self.threads = threads
        self.batch_size = batch_size
        self.interval = interval
        
        # 生成模拟用户ID列表
        self.user_ids = [f"user-{str(uuid.uuid4())[:8]}" for _ in range(total_users)]
        
        # 生成模拟壁纸ID列表
        self.wallpaper_ids = [f"wallpaper-{str(uuid.uuid4())[:8]}" for _ in range(total_wallpapers)]
        
        # 标记热门壁纸
        hot_count = int(total_wallpapers * HOT_WALLPAPERS_PERCENTAGE)
        self.hot_wallpapers = set(random.sample(self.wallpaper_ids, hot_count))
        
        # 标记活跃用户
        active_count = int(total_users * ACTIVE_USERS_PERCENTAGE)
        self.active_users = set(random.sample(self.user_ids, active_count))
        
        # 统计数据
        self.message_count = 0
        self.start_time = None
        self.stop_flag = threading.Event()
        
        # 创建Kafka生产者
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            batch_size=16384,  # 增大批次大小以提高吞吐量
            linger_ms=5,       # 等待聚合更多消息
            compression_type="gzip"  # 启用压缩
        )
        
        print(f"已初始化 Kafka 模拟生成器:")
        print(f"- Kafka Brokers: {KAFKA_BROKERS}")
        print(f"- Kafka Topic: {KAFKA_TOPIC}")
        print(f"- 模拟用户数: {total_users} (活跃用户: {active_count})")
        print(f"- 模拟壁纸数: {total_wallpapers} (热门壁纸: {hot_count})")
        print(f"- 生产者线程数: {threads}")
        print(f"- 每批次消息数: {batch_size}")
        print(f"- 批次间隔: {interval} 秒")
    
    def _select_user_id(self) -> str:
        """智能选择一个用户ID，有更高概率选择活跃用户"""
        if random.random() < 0.7:  # 70%的概率选择活跃用户
            if self.active_users:
                return random.choice(list(self.active_users))
        return random.choice(self.user_ids)
    
    def _select_wallpaper_id(self) -> str:
        """智能选择一个壁纸ID，有更高概率选择热门壁纸"""
        if random.random() < 0.8:  # 80%的概率选择热门壁纸
            if self.hot_wallpapers:
                return random.choice(list(self.hot_wallpapers))
        return random.choice(self.wallpaper_ids)
    
    def _select_weight(self) -> float:
        """根据权重分布随机选择一个权重值"""
        # 使用累积概率分布选择权重
        r = random.random()
        cumulative_prob = 0.0
        
        for weight, prob in INTERACTION_WEIGHTS:
            cumulative_prob += prob
            if r <= cumulative_prob:
                return weight
                
        # 如果执行到这里(不应该)，使用最后一个权重
        return INTERACTION_WEIGHTS[-1][0]
    
    def _generate_message(self) -> Dict:
        """生成一条模拟消息"""
        user_id = self._select_user_id()
        wallpaper_id = self._select_wallpaper_id()
        weight = self._select_weight()
        
        # 80%的情况下使用当前时间，20%的情况下使用稍微早一些的时间
        if random.random() < 0.8:
            collected_at = datetime.now().isoformat()
        else:
            # 随机生成过去5分钟内的时间
            seconds_ago = random.randint(1, 300)
            collected_at = (datetime.now().timestamp() - seconds_ago)
            collected_at = datetime.fromtimestamp(collected_at).isoformat()
        
        # 生成符合trending-analyzer期望格式的消息
        return {
            "userId": user_id,
            "wallpaperId": wallpaper_id,
            "weight": weight,
            "collectedAt": collected_at
        }
    
    def _producer_thread(self, thread_id: int):
        """生产者线程函数，不断生成并发送消息批次"""
        local_count = 0
        
        while not self.stop_flag.is_set():
            batch_messages = []
            
            # 生成一批次消息
            for _ in range(self.batch_size):
                message = self._generate_message()
                batch_messages.append(message)
            
            # 发送批次消息
            for message in batch_messages:
                try:
                    self.producer.send(KAFKA_TOPIC, message)
                    local_count += 1
                except KafkaError as e:
                    print(f"线程 {thread_id} 发送消息错误: {e}")
            
            # 每批次后等待短暂时间，避免过载
            time.sleep(self.interval)
            
            # 定期记录统计信息
            if local_count >= 1000:
                with self._lock:
                    self.message_count += local_count
                local_count = 0
                
                # 计算并显示当前速率
                if self.start_time:
                    elapsed = time.time() - self.start_time
                    rate = self.message_count / elapsed if elapsed > 0 else 0
                    print(f"线程 {thread_id} - 已发送 {local_count} 条消息，总计 {self.message_count} 条，速率 {rate:.2f} 条/秒")
        
        # 线程结束前汇总剩余统计数据
        with self._lock:
            self.message_count += local_count
    
    def start(self, duration: Optional[int] = None):
        """启动模拟生成器"""
        self._lock = threading.Lock()
        self.message_count = 0
        self.start_time = time.time()
        self.stop_flag.clear()
        
        # 创建并启动生产者线程
        threads = []
        for i in range(self.threads):
            t = threading.Thread(target=self._producer_thread, args=(i,))
            t.daemon = True  # 设为守护线程，主线程结束时自动终止
            t.start()
            threads.append(t)
            
        print(f"已启动 {self.threads} 个生产者线程")
        
        try:
            if duration:
                # 运行指定时间后停止
                print(f"将运行 {duration} 秒...")
                time.sleep(duration)
                self.stop()
            else:
                # 无限运行，直到手动中断
                print("按 Ctrl+C 停止...")
                while True:
                    time.sleep(1)
        except KeyboardInterrupt:
            print("\n接收到中断信号，正在停止...")
            self.stop()
        
        # 等待所有线程结束
        for t in threads:
            t.join(timeout=2)
    
    def stop(self):
        """停止模拟生成器"""
        # 设置停止标志
        self.stop_flag.set()
        
        # 等待生产者完成任何挂起的发送
        print("等待生产者完成发送...")
        self.producer.flush()
        
        # 关闭生产者
        self.producer.close()
        
        # 显示最终统计信息
        elapsed = time.time() - self.start_time
        rate = self.message_count / elapsed if elapsed > 0 else 0
        
        print("\n============ 运行统计 ============")
        print(f"总运行时间: {elapsed:.2f} 秒")
        print(f"总发送消息: {self.message_count} 条")
        print(f"平均发送速率: {rate:.2f} 条/秒")
        print("==================================")

def main():
    """主函数，解析命令行参数并启动生成器"""
    parser = argparse.ArgumentParser(description="Kafka 模拟数据生成器")
    parser.add_argument("--users", type=int, default=DEFAULT_TOTAL_USERS, help=f"模拟用户数量 (默认: {DEFAULT_TOTAL_USERS})")
    parser.add_argument("--wallpapers", type=int, default=DEFAULT_TOTAL_WALLPAPERS, help=f"模拟壁纸数量 (默认: {DEFAULT_TOTAL_WALLPAPERS})")
    parser.add_argument("--threads", type=int, default=DEFAULT_THREADS, help=f"生产者线程数 (默认: {DEFAULT_THREADS})")
    parser.add_argument("--batch", type=int, default=DEFAULT_BATCH_SIZE, help=f"每批次消息数 (默认: {DEFAULT_BATCH_SIZE})")
    parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL, help=f"批次间隔秒数 (默认: {DEFAULT_INTERVAL})")
    parser.add_argument("--duration", type=int, help="运行持续时间(秒)，不指定则无限运行")
    args = parser.parse_args()
    
    # 创建并启动生成器
    generator = KafkaStubGenerator(
        total_users=args.users,
        total_wallpapers=args.wallpapers,
        threads=args.threads,
        batch_size=args.batch,
        interval=args.interval
    )
    
    # 启动生成器
    generator.start(duration=args.duration)

if __name__ == "__main__":
    main() 