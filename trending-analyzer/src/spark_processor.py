import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, sum as _sum, desc, expr
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, DoubleType
from pyspark.sql.window import Window

from . import config
from .redis_utils import update_trending_wallpapers

logger = logging.getLogger(__name__)

def get_spark_session():
    """Initializes and returns a SparkSession."""
    try:
        # 注意：对于生产环境，请正确配置包，例如通过 spark-submit
        # 使用 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:YOUR_SPARK_VERSION
        spark = (
            SparkSession.builder
            .appName(config.SPARK_APP_NAME)
            .master(config.SPARK_MASTER)
            # 为生产环境配置合适的 checkpoint 目录
            .config("spark.sql.streaming.checkpointLocation", "/tmp/spark_checkpoints_trending")
            .getOrCreate()
        )
        logger.info("SparkSession 创建成功。")
        return spark
    except Exception as e:
        logger.error(f"创建 SparkSession 时出错: {e}", exc_info=True)
        raise

def define_kafka_schema():
    """
    Defines the expected schema of the JSON messages from the Kafka topic
    based on interaction-collector/README.md.
    """
    return StructType([
        StructField("userId", StringType(), True),
        StructField("wallpaperId", StringType(), True),
        # Weight 代表分值的 *变化量*，可以是 float/double 类型
        StructField("weight", DoubleType(), True),
        StructField("collectedAt", TimestampType(), True) # 为了清晰，从 timestamp 重命名而来
    ])

def process_stream(spark: SparkSession):
    """
    Sets up and runs the Spark Streaming pipeline.
    """
    schema = define_kafka_schema()

    # 1. 从 Kafka 读取数据
    kafka_df = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", config.KAFKA_BROKERS)
        .option("subscribe", config.KAFKA_TOPIC)
        .option("startingOffsets", "latest") # 只处理新消息
        .option("failOnDataLoss", "false") # 处理潜在的数据丢失
        .load()
    )

    # 2. 解析 JSON 消息
    # 假设 Kafka 消息的值是 JSON 字符串
    parsed_df = (
        kafka_df
        .selectExpr("CAST(value AS STRING)")
        .select(from_json(col("value"), schema).alias("data"))
        .select("data.*")
        # 如果需要，重命名列以保持一致性（可选）
        .withColumnRenamed("userId", "user_id")
        .withColumnRenamed("wallpaperId", "wallpaper_id")
        .withColumnRenamed("collectedAt", "timestamp") # 保留 timestamp 用于窗口计算
    )

    # 添加水印以处理延迟数据（根据预期的延迟调整）
    # 示例：允许数据延迟 10 分钟
    # 使用从 'collectedAt' 派生出的 'timestamp' 列
    parsed_df_with_watermark = parsed_df.withWatermark("timestamp", "10 minutes")

    # 3. 滑动窗口聚合 - 直接对 'weight' 字段求和
    window_duration = f"{config.WINDOW_DURATION_SECONDS} seconds"
    slide_duration = f"{config.SLIDE_DURATION_SECONDS} seconds"

    # 按窗口和 wallpaper_id 分组，对权重变化量求和
    windowed_agg_df = (
        parsed_df_with_watermark
        .groupBy(
            window(col("timestamp"), window_duration, slide_duration),
            col("wallpaper_id")
        )
        # 直接对 'weight' (分数差值) 求和
        .agg(_sum("weight").alias("total_score_change")) # 或者如果倾向用 'score' 也可以
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
    rank_window_spec = Window.partitionBy("window").orderBy(desc("total_score_change"))

    ranked_df = (
        windowed_agg_df
        # 在定义的窗口规范上使用 rank() 函数
        .withColumn("rank", expr("rank() OVER (PARTITION BY window ORDER BY total_score_change DESC)"))
        .filter(col("rank") <= config.TOP_N)
        .select(
            col("window.start").alias("window_start"),
            col("window.end").alias("window_end"),
            col("wallpaper_id"),
            col("total_score_change").alias("score") # 为了 Redis 输出的一致性而重命名
        )
     )

    # 5. 将结果写入 Redis (使用 foreachBatch)
    query = (
        ranked_df.writeStream
        .outputMode("complete") # 使用 'complete' 因为我们在每个窗口内重新计算排名
        .foreachBatch(update_trending_wallpapers) # 传递函数引用
        .option("checkpointLocation", spark.conf.get("spark.sql.streaming.checkpointLocation"))
        .start()
    )

    logger.info("流处理查询已启动。等待终止...")
    query.awaitTermination() 