#!/usr/bin/env python
"""
简单脚本，用于测试 Kafka 连接是否正常工作
"""
import sys
import json
from datetime import datetime
from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import KafkaError, NoBrokersAvailable

# Kafka 配置
KAFKA_BROKERS = "localhost:9092"
KAFKA_TOPIC = "interaction_collected"  # 与 trending-analyzer 使用的同一个主题

def test_admin_connection():
    """测试管理连接，创建或检查主题"""
    print(f"尝试连接到 Kafka 管理接口: {KAFKA_BROKERS}")
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=KAFKA_BROKERS,
            client_id='test-admin-client'
        )
        
        # 获取现有主题
        topics = admin_client.list_topics()
        print(f"现有的主题: {topics}")
        
        # 如果测试主题不存在，则创建它
        if KAFKA_TOPIC not in topics:
            print(f"创建主题: {KAFKA_TOPIC}")
            new_topic = NewTopic(
                name=KAFKA_TOPIC,
                num_partitions=1,
                replication_factor=1
            )
            admin_client.create_topics([new_topic])
            print(f"成功创建主题: {KAFKA_TOPIC}")
        else:
            print(f"主题已存在: {KAFKA_TOPIC}")
            
        admin_client.close()
        return True
    except NoBrokersAvailable:
        print("❌ 无法连接到 Kafka broker。请检查 Kafka 服务是否运行。")
        return False
    except Exception as e:
        print(f"❌ 管理客户端连接错误: {e}")
        return False

def test_producer():
    """测试生产者连接，发送测试消息"""
    print(f"\n尝试连接到 Kafka 生产者: {KAFKA_BROKERS}")
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        # 创建测试消息
        test_message = {
            "userId": "test-user-123",
            "wallpaperId": "test-wallpaper-456",
            "weight": 10.5,
            "collectedAt": datetime.now().isoformat()
        }
        
        # 发送消息
        future = producer.send(KAFKA_TOPIC, test_message)
        result = future.get(timeout=10)  # 等待发送确认
        
        print(f"✅ 消息已成功发送到分区 {result.partition}, 偏移量 {result.offset}")
        producer.close()
        return True
    except KafkaError as e:
        print(f"❌ Kafka 生产者错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 生产者连接错误: {e}")
        return False

def test_consumer():
    """测试消费者连接，尝试读取消息"""
    print(f"\n尝试连接到 Kafka 消费者: {KAFKA_BROKERS}")
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BROKERS,
            auto_offset_reset='earliest',
            group_id='test-consumer-group',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            consumer_timeout_ms=10000  # 10秒超时
        )
        
        print(f"等待 10 秒以接收来自 {KAFKA_TOPIC} 的消息...")
        
        message_received = False
        for message in consumer:
            print(f"收到消息:")
            print(f"  主题: {message.topic}")
            print(f"  分区: {message.partition}")
            print(f"  偏移量: {message.offset}")
            print(f"  键: {message.key}")
            print(f"  值: {message.value}")
            message_received = True
            break  # 只读取一条消息
            
        if not message_received:
            print("⚠️ 在指定的超时时间内没有收到消息。这可能是正常的，如果没有足够的消息。")
        
        consumer.close()
        return True
    except KafkaError as e:
        print(f"❌ Kafka 消费者错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 消费者连接错误: {e}")
        return False

def main():
    """主函数"""
    print("==================== Kafka 连接测试 ====================")
    
    admin_ok = test_admin_connection()
    if not admin_ok:
        print("❌ 管理员连接测试失败，跳过其他测试。")
        return
        
    producer_ok = test_producer()
    if not producer_ok:
        print("❌ 生产者连接测试失败，跳过消费者测试。")
        return
        
    consumer_ok = test_consumer()
    
    print("\n==================== 测试结果 ====================")
    print(f"管理连接: {'✅ 成功' if admin_ok else '❌ 失败'}")
    print(f"生产者连接: {'✅ 成功' if producer_ok else '❌ 失败'}")
    print(f"消费者连接: {'✅ 成功' if consumer_ok else '❌ 失败'}")
    
    if admin_ok and producer_ok and consumer_ok:
        print("\n✅ 全部测试通过！Kafka 连接正常工作。")
    else:
        print("\n❌ 部分测试失败。请检查错误信息。")

if __name__ == "__main__":
    main() 