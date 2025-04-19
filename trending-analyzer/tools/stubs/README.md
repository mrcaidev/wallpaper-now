# Kafka 模拟数据生成器

这个工具用于生成高频率、大数据量的模拟壁纸用户互动数据，并发送到Kafka，用于测试trending-analyzer流处理系统。

## 功能特点

- **高吞吐量**: 使用多线程和批处理方式生成和发送消息
- **真实数据分布**: 模拟真实用户行为特点，包括热门壁纸、活跃用户、不同权重的互动
- **可配置参数**: 支持控制用户数量、壁纸数量、发送速率等参数
- **实时统计**: 提供实时发送速率和总量统计

## 安装依赖

确保已安装所需依赖：

```bash
pip install kafka-python python-dotenv
```

## 使用方法

### 基本用法

直接运行脚本，使用默认参数：

```bash
python kafka_stub_generator.py
```

按Ctrl+C停止运行。

### 自定义参数

```bash
python kafka_stub_generator.py --users 2000 --wallpapers 1000 --threads 10 --batch 200 --interval 0.05 --duration 300
```

### 参数说明

- `--users`: 模拟用户数量（默认: 1000）
- `--wallpapers`: 模拟壁纸数量（默认: 500）
- `--threads`: 生产者线程数（默认: 5）
- `--batch`: 每批次消息数（默认: 100）
- `--interval`: 批次间隔秒数（默认: 0.1）
- `--duration`: 运行持续时间(秒)，不指定则无限运行

## 消息格式

生成的消息遵循trending-analyzer项目期望的格式：

```json
{
  "userId": "user-abc123",
  "wallpaperId": "wallpaper-def456",
  "weight": 5.0,
  "collectedAt": "2025-01-01T12:34:56.789"
}
```

## 权重分布

消息中的`weight`字段表示不同类型的互动行为对壁纸热度的影响：

- 1.0: 浏览 (45%概率)
- 2.0: 点赞 (25%概率)
- 5.0: 下载 (15%概率)
- 7.0: 收藏 (8%概率)
- 10.0: 设为桌面背景 (5%概率)
- -0.5: 取消点赞/收藏 (2%概率)

## 使用场景

1. **压力测试**: 测试trending-analyzer处理高流量数据的能力
2. **功能验证**: 验证热门壁纸排名算法是否正确
3. **演示**: 在没有真实用户数据时用于演示系统功能
4. **开发**: 在开发环境中提供稳定的测试数据流

## 示例用法

### 短时间大批量测试

```bash
# 使用10个线程，每0.01秒发送200条消息，运行30秒
python kafka_stub_generator.py --threads 10 --interval 0.01 --batch 200 --duration 30
```

### 长时间低负载测试

```bash
# 使用2个线程，每0.5秒发送50条消息，无限运行
python kafka_stub_generator.py --threads 2 --interval 0.5 --batch 50
```

### 在Docker环境中测试

如果您在Docker中运行Kafka，请确保在`.env`文件中正确设置`KAFKA_BROKERS`地址。 