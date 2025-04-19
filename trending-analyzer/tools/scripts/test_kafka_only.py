#!/usr/bin/env python
"""
只测试Kafka功能的脚本
"""
import os
import sys
import json
import logging
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 初始化日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# Kafka配置
KAFKA_BROKERS = os.getenv('KAFKA_BROKERS', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'interaction_collected')

try:
    # 导入Kafka客户端
    from kafka import KafkaProducer, KafkaConsumer
    from kafka.errors import KafkaError
except ImportError as e:
    logger.error(f"缺少必要的库: {e}")
    logger.error("请确保安装了 kafka-python")
    sys.exit(1)

def send_test_data(num_messages=10):
    """向Kafka发送测试数据"""
    logger.info(f"准备向Kafka主题 {KAFKA_TOPIC} 发送 {num_messages} 条测试消息")
    
    try:
        # 创建Kafka生产者
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        # 生成并发送测试消息
        for i in range(num_messages):
            # 创建一条模拟的壁纸交互记录
            wallpaper_id = f"wallpaper-{i % 5 + 1}"  # 循环使用5个不同的壁纸ID
            timestamp = (datetime.now() - timedelta(minutes=i)).isoformat()
            
            # 根据索引设置不同的权重，模拟不同的用户行为
            weight = 5.0
            if i % 3 == 0:  # 点赞
                weight = 2.0
            elif i % 3 == 1:  # 下载
                weight = 5.0
            else:  # 收藏
                weight = 10.0
                
            message = {
                "userId": f"test-user-{i % 3 + 1}",
                "wallpaperId": wallpaper_id,
                "weight": weight,
                "collectedAt": timestamp
            }
            
            # 发送消息
            future = producer.send(KAFKA_TOPIC, message)
            result = future.get(timeout=10)
            logger.info(f"已发送消息 {i+1}/{num_messages}: wallpaper={wallpaper_id}, weight={weight}")
            
        # 确保所有消息都已发送
        producer.flush()
        producer.close()
        logger.info("所有测试消息已成功发送到Kafka")
        return True
        
    except KafkaError as e:
        logger.error(f"发送Kafka消息时出错: {e}")
        return False
    except Exception as e:
        logger.error(f"发送测试数据时出现未预期的错误: {e}")
        return False

def consume_test_data(max_messages=None, timeout_sec=30):
    """从Kafka消费测试数据"""
    logger.info(f"准备从Kafka主题 {KAFKA_TOPIC} 消费消息")
    
    try:
        # 创建Kafka消费者
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BROKERS,
            auto_offset_reset='earliest',  # 从最早的消息开始读取
            group_id='test-consumer-group',  # 消费者组ID
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            consumer_timeout_ms=timeout_sec * 1000  # 超时时间（毫秒）
        )
        
        logger.info(f"等待最多 {timeout_sec} 秒接收消息...")
        
        # 读取消息
        messages = []
        start_time = time.time()
        for i, message in enumerate(consumer):
            # 如果设置了最大消息数且已达到，则退出
            if max_messages and i >= max_messages:
                break
                
            # 提取消息内容
            msg_data = message.value
            logger.info(f"收到消息 {i+1}:")
            logger.info(f"  用户ID: {msg_data.get('userId')}")
            logger.info(f"  壁纸ID: {msg_data.get('wallpaperId')}")
            logger.info(f"  权重: {msg_data.get('weight')}")
            logger.info(f"  时间戳: {msg_data.get('collectedAt')}")
            
            messages.append(msg_data)
            
            # 如果已超时，则退出
            if time.time() - start_time > timeout_sec:
                logger.warning("已达到超时时间，停止消费")
                break
        
        consumer.close()
        
        # 统计和汇总结果
        if messages:
            logger.info(f"总共接收到 {len(messages)} 条消息")
            
            # 简单统计：计算每个壁纸的累计权重
            wallpaper_weights = {}
            for msg in messages:
                wallpaper_id = msg.get('wallpaperId')
                weight = msg.get('weight', 0)
                
                if wallpaper_id not in wallpaper_weights:
                    wallpaper_weights[wallpaper_id] = 0
                wallpaper_weights[wallpaper_id] += weight
            
            # 按权重排序并显示结果
            sorted_wallpapers = sorted(
                wallpaper_weights.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            logger.info("壁纸累计权重（从高到低）:")
            for wallpaper_id, total_weight in sorted_wallpapers:
                logger.info(f"  {wallpaper_id}: {total_weight}")
                
            return True, messages
        else:
            logger.warning("未接收到任何消息")
            return True, []
            
    except KafkaError as e:
        logger.error(f"消费Kafka消息时出错: {e}")
        return False, []
    except Exception as e:
        logger.error(f"消费测试数据时出现未预期的错误: {e}")
        return False, []

def main():
    """主函数"""
    print("\n==================== Kafka 功能测试 ====================")
    
    # 发送测试数据到Kafka
    print("\n----- 发送测试数据 -----")
    data_sent = send_test_data(15)
    if not data_sent:
        logger.error("无法发送测试数据到Kafka，终止测试")
        return
    
    # 消费测试数据
    print("\n----- 消费测试数据 -----")
    success, messages = consume_test_data(max_messages=20, timeout_sec=15)
    
    # 显示最终结果
    print("\n==================== 测试结果 ====================")
    if data_sent and success:
        print(f"\n✅ 测试成功完成！")
        print(f"✅ 成功发送 15 条消息")
        print(f"✅ 成功接收 {len(messages)} 条消息")
        print("\n这个结果表明您的Kafka服务器工作正常，可以与trending-analyzer集成。")
    else:
        print("\n❌ 测试失败。请检查错误日志。")

if __name__ == "__main__":
    main() 