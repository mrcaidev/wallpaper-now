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
        # Note: For production, configure packages properly, e.g., via spark-submit
        # Use --packages org.apache.spark:spark-sql-kafka-0-10_2.12:YOUR_SPARK_VERSION
        spark = (
            SparkSession.builder
            .appName(config.SPARK_APP_NAME)
            .master(config.SPARK_MASTER)
            # Configure proper checkpoint dir for production
            .config("spark.sql.streaming.checkpointLocation", "/tmp/spark_checkpoints_trending")
            .getOrCreate()
        )
        logger.info("SparkSession created successfully.")
        return spark
    except Exception as e:
        logger.error(f"Error creating SparkSession: {e}", exc_info=True)
        raise

def define_kafka_schema():
    """
    Defines the expected schema of the JSON messages from the Kafka topic
    based on interaction-collector/README.md.
    """
    return StructType([
        StructField("userId", StringType(), True),
        StructField("wallpaperId", StringType(), True),
        # Weight represents the CHANGE in score, can be float/double
        StructField("weight", DoubleType(), True),
        StructField("collectedAt", TimestampType(), True) # Renamed from timestamp for clarity
    ])

def process_stream(spark: SparkSession):
    """
    Sets up and runs the Spark Streaming pipeline.
    """
    schema = define_kafka_schema()

    # 1. Read from Kafka
    kafka_df = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", config.KAFKA_BROKERS)
        .option("subscribe", config.KAFKA_TOPIC)
        .option("startingOffsets", "latest") # Process only new messages
        .option("failOnDataLoss", "false") # Handle potential data loss
        .load()
    )

    # 2. Parse JSON messages
    # Assuming the Kafka message value is a JSON string
    parsed_df = (
        kafka_df
        .selectExpr("CAST(value AS STRING)")
        .select(from_json(col("value"), schema).alias("data"))
        .select("data.*")
        # Rename columns for consistency if desired (optional)
        .withColumnRenamed("userId", "user_id")
        .withColumnRenamed("wallpaperId", "wallpaper_id")
        .withColumnRenamed("collectedAt", "timestamp") # Keep timestamp for windowing
    )

    # Add watermark for handling late data (adjust based on expected lateness)
    # Example: Allow data to be 10 minutes late
    # Use the 'timestamp' column derived from 'collectedAt'
    parsed_df_with_watermark = parsed_df.withWatermark("timestamp", "10 minutes")

    # 3. Sliding Window Aggregation - Directly sum the 'weight' field
    window_duration = f"{config.WINDOW_DURATION_SECONDS} seconds"
    slide_duration = f"{config.SLIDE_DURATION_SECONDS} seconds"

    # Group by window and wallpaper_id, summing the weight changes
    windowed_agg_df = (
        parsed_df_with_watermark
        .groupBy(
            window(col("timestamp"), window_duration, slide_duration),
            col("wallpaper_id")
        )
        # Sum the 'weight' (score difference) directly
        .agg(_sum("weight").alias("total_score_change")) # Or just 'score' if preferred
    )

    # IMPORTANT: The 'total_score_change' represents the sum of weight *changes*
    # within the window. This might not be the absolute trending score you want
    # unless the upstream interaction collector guarantees sending initial states.
    # If you need an *absolute* score, the logic might need to be more complex,
    # potentially involving state management (e.g., mapGroupsWithState) or
    # assuming the window captures enough history to approximate the current state.
    # For now, we proceed assuming summing the changes is the desired logic.
    # If absolute score is needed, this aggregation part needs rethinking.

    # 4. Rank Wallpapers within each window based on the aggregated score change
    # Define window specification for ranking
    rank_window_spec = Window.partitionBy("window").orderBy(desc("total_score_change"))

    ranked_df = (
        windowed_agg_df
        # Use rank() function over the defined window spec
        .withColumn("rank", expr("rank() OVER (PARTITION BY window ORDER BY total_score_change DESC)"))
        .filter(col("rank") <= config.TOP_N)
        .select(
            col("window.start").alias("window_start"),
            col("window.end").alias("window_end"),
            col("wallpaper_id"),
            col("total_score_change").alias("score") # Rename for consistency in Redis output
        )
     )

    # 5. Write results to Redis (using foreachBatch)
    query = (
        ranked_df.writeStream
        .outputMode("complete") # Use 'complete' as we rank within each window
        .foreachBatch(update_trending_wallpapers) # Pass the function reference
        .option("checkpointLocation", spark.conf.get("spark.sql.streaming.checkpointLocation"))
        .start()
    )

    logger.info("Streaming query started. Waiting for termination...")
    query.awaitTermination() 