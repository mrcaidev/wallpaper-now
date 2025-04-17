import logging
import sys
from src.spark_processor import get_spark_session, process_stream

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    logger.info("启动趋势壁纸分析器...")
    spark = None
    try:
        # 获取 Spark Session
        spark = get_spark_session()

        # 开始处理流数据
        process_stream(spark)

    except Exception as e:
        logger.critical(f"发生意外错误: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if spark:
            logger.info("停止 SparkSession...")
            spark.stop()
            logger.info("SparkSession 已停止。")
        logger.info("趋势壁纸分析器已结束。")

if __name__ == "__main__":
    main() 