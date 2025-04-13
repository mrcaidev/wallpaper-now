import logging
import sys
from src.spark_processor import get_spark_session, process_stream

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Trending Wallpaper Analyzer...")
    spark = None
    try:
        # Get Spark Session
        spark = get_spark_session()

        # Start processing the stream
        process_stream(spark)

    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if spark:
            logger.info("Stopping SparkSession...")
            spark.stop()
            logger.info("SparkSession stopped.")
        logger.info("Trending Wallpaper Analyzer finished.")

if __name__ == "__main__":
    main() 