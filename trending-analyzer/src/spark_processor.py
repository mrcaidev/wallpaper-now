import logging  # 导入日志模块
from pyspark.sql import SparkSession  # 从 PySpark SQL 模块导入 SparkSession
from pyspark.sql.functions import from_json, col, window, sum as _sum, desc, expr  # 从 PySpark SQL 函数模块导入所需函数
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, DoubleType # 从 PySpark SQL 类型模块导入所需类型
from pyspark.sql.window import Window  # 从 PySpark SQL 窗口模块导入 Window

import config  # 导入 config 模块
from redis_utils import update_trending_wallpapers  # 从 redis_utils 模块导入更新函数

logger = logging.getLogger(__name__) # 获取当前模块的 logger 实例

# --- 互动权重已移除 ---
# 权重直接来自 Kafka 消息

def get_spark_session():  # 定义获取 SparkSession 的函数
    """Initializes and returns a SparkSession."""  # 函数文档字符串
    try:  # 开始异常处理块
        # 注意：对于生产环境，请正确配置包，例如通过 spark-submit
        # 使用 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:YOUR_SPARK_VERSION
        spark = (  # 开始构建 SparkSession
            SparkSession.builder
            .appName(config.SPARK_APP_NAME)  # 设置应用名称
            .master(config.SPARK_MASTER)  # 设置 Spark Master URL
            # 为生产环境配置合适的 checkpoint 目录
            .config("spark.sql.streaming.checkpointLocation", "/tmp/spark_checkpoints_trending") # 配置检查点目录
            # 添加Kafka连接器 - 自动下载方式，方便打包镜像
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0")
            .getOrCreate()  # 获取或创建 SparkSession 实例
        )
        logger.info("SparkSession 创建成功。")
        return spark  # 返回创建的 SparkSession
    except Exception as e:  # 捕获所有异常
        logger.error(f"创建 SparkSession 时出错: {e}", exc_info=True)
        raise  # 重新抛出异常

def define_kafka_schema():  # 定义 Kafka 消息 Schema 的函数
    """
    Defines the expected schema of the JSON messages from the Kafka topic
    based on interaction-collector/README.md.
    """  # 函数文档字符串
    return StructType([  # 返回一个 StructType 对象，定义 Schema 结构
        StructField("userId", StringType(), True),  # 定义 userId 字段，字符串类型，可为空
        StructField("wallpaperId", StringType(), True),  # 定义 wallpaperId 字段，字符串类型，可为空
        # Weight 代表分值的 *变化量*，可以是 float/double 类型
        StructField("weight", DoubleType(), True),  # 定义 weight 字段，双精度浮点类型，可为空
        StructField("collectedAt", TimestampType(), True) # 定义 collectedAt 字段，时间戳类型，可为空
    ])

# --- calculate_interaction_score 函数已移除 ---

def process_stream(spark: SparkSession):  # 定义处理数据流的主函数，接收 SparkSession 作为参数
    """
    Sets up and runs the Spark Streaming pipeline.
    """  # 函数文档字符串
    schema = define_kafka_schema()  # 调用函数获取 Kafka 消息的 Schema

    # 1. 从 Kafka 读取数据
    kafka_df = (  # 开始读取 Kafka 数据流
        spark.readStream  # 创建 DataStreamReader
        .format("kafka")  # 指定数据源格式为 Kafka
        .option("kafka.bootstrap.servers", config.KAFKA_BROKERS)  # 设置 Kafka 服务器地址
        .option("subscribe", config.KAFKA_TOPIC)  # 设置要订阅的 Kafka 主题
        .option("startingOffsets", "latest") # 设置从最新的偏移量开始读取
        .option("failOnDataLoss", "false") # 设置在数据丢失时不失败
        .load()  # 加载数据流，返回 DataFrame
    )

    # 2. 解析 JSON 消息
    # 假设 Kafka 消息的值是 JSON 字符串
    parsed_df = (  # 开始解析 JSON 数据
        kafka_df
        .selectExpr("CAST(value AS STRING)")  # 将 Kafka 消息的值（二进制）转换为字符串
        .select(from_json(col("value"), schema).alias("data"))  # 使用定义的 Schema 解析 JSON 字符串，并将结果放入名为 'data' 的结构体列中
        .select("data.*")  # 将 'data' 结构体中的所有字段提取为顶级列
        # 如果需要，重命名列以保持一致性（可选）
        .withColumnRenamed("userId", "user_id")  # 重命名列 userId 为 user_id
        .withColumnRenamed("wallpaperId", "wallpaper_id")  # 重命名列 wallpaperId 为 wallpaper_id
        .withColumnRenamed("collectedAt", "timestamp") # 重命名列 collectedAt 为 timestamp，用于窗口计算
    )

    # 添加水印以处理延迟数据（根据预期的延迟调整）
    # 示例：允许数据延迟 10 分钟
    # 使用从 'collectedAt' 派生出的 'timestamp' 列
    parsed_df_with_watermark = parsed_df.withWatermark("timestamp", "10 minutes") # 在 timestamp 列上设置 10 分钟的水印

    # 3. 滑动窗口聚合 - 直接对 'weight' 字段求和
    window_duration = f"{config.WINDOW_DURATION_SECONDS} seconds"  # 定义窗口持续时间字符串
    slide_duration = f"{config.SLIDE_DURATION_SECONDS} seconds"  # 定义滑动间隔时间字符串

    # 按窗口和 wallpaper_id 分组，对权重变化量求和
    windowed_agg_df = (  # 开始进行窗口聚合
        parsed_df_with_watermark
        .groupBy(  # 按以下列进行分组
            window(col("timestamp"), window_duration, slide_duration),  # 按时间戳列进行滑动窗口分组
            col("wallpaper_id")  # 按壁纸 ID 分组
        )
        # 直接对 'weight' (分数差值) 求和
        .agg(_sum("weight").alias("total_score_change")) # 对每个分组内的 weight 列求和，并将结果命名为 total_score_change
    )

    # 重要提示：这里的 'total_score_change' 代表窗口内权重 *变化量* 的总和。
    # 这可能不是你想要的绝对趋势分数，除非上游的 interaction collector 保证发送初始状态。
    # 如果你需要 *绝对* 分数，逻辑可能需要更复杂，
    # 可能涉及状态管理（例如，mapGroupsWithState）或
    # 假设窗口捕获了足够的历史记录来近似当前状态。
    # 目前，我们假设对变化量求和是所需的逻辑。
    # 如果需要绝对分数，则需要重新考虑聚合部分。

    # 4. 基于聚合的分数变化量，在每个窗口内对壁纸进行排名
    # 定义排名用的窗口规范
    rank_window_spec = Window.partitionBy("window").orderBy(desc("total_score_change")) # 定义窗口函数：按窗口分区，按 total_score_change 降序排序

    ranked_df = (  # 开始计算排名
        windowed_agg_df
        # 在定义的窗口规范上使用 rank() 函数
        .withColumn("rank", expr("rank() OVER (PARTITION BY window ORDER BY total_score_change DESC)")) # 添加排名列，使用 rank 函数和定义的窗口规范
        .filter(col("rank") <= config.TOP_N)  # 筛选出排名在前 N 的记录
        .select(  # 选择最终需要的列
            col("window.start").alias("window_start"),  # 选择窗口起始时间，重命名为 window_start
            col("window.end").alias("window_end"),  # 选择窗口结束时间，重命名为 window_end
            col("wallpaper_id"),  # 选择壁纸 ID
            col("total_score_change").alias("score") # 选择聚合分数，为了 Redis 输出的一致性而重命名为 score
        )
     )

    # 5. 将结果写入 Redis (使用 foreachBatch)
    query = (  # 开始定义流式写入操作
        ranked_df.writeStream  # 创建 DataStreamWriter
        .outputMode("complete") # 设置输出模式为 Complete (每次输出完整的聚合结果)
        .foreachBatch(update_trending_wallpapers) # 对每个微批次应用自定义的写入 Redis 函数
        .option("checkpointLocation", spark.conf.get("spark.sql.streaming.checkpointLocation")) # 设置检查点位置，从 Spark 配置中获取
        .start()  # 启动流式查询
    )

    logger.info("流处理查询已启动。等待终止...")
    query.awaitTermination() # 阻塞当前线程，直到流式查询终止 