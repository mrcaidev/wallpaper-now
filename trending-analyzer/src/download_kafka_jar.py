"""
下载Spark Kafka连接器JAR文件
"""
from pyspark.sql import SparkSession

print("正在初始化SparkSession并下载Kafka连接器...")

# 创建SparkSession并配置Kafka连接器
spark = SparkSession.builder \
    .appName("DownloadKafkaConnector") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0") \
    .getOrCreate()

print("Kafka连接器已下载完成！")
spark.stop()
print("SparkSession已关闭。") 