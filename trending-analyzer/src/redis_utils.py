import redis
import logging
from pyspark.sql import Row
from . import config

logger = logging.getLogger(__name__)

redis_client = None

def get_redis_client():
    """Initializes and returns a Redis client connection."""
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.StrictRedis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                db=config.REDIS_DB,
                decode_responses=True # Decode responses to strings
            )
            redis_client.ping() # Check connection
            logger.info(f"Successfully connected to Redis at {config.REDIS_HOST}:{config.REDIS_PORT}")
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    return redis_client

def update_trending_wallpapers(batch_df):
    """
    Updates the trending wallpapers sorted set in Redis based on the batch DataFrame.
    Assumes batch_df contains columns 'wallpaper_id' and 'score'.
    """
    try:
        r = get_redis_client()
        if not r:
            logger.error("Redis client not available, skipping update.")
            return

        # Convert Spark DataFrame rows to dictionary for Redis ZADD
        # Collect data to driver - be mindful of potential memory issues with large batches
        trending_data = batch_df.rdd.map(lambda row: (row.wallpaper_id, row.score)).collect()

        if not trending_data:
            logger.info("No trending data in this batch to update Redis.")
            return

        # Use a pipeline for atomic updates
        pipe = r.pipeline()
        # Clear the existing sorted set before adding new data
        pipe.delete(config.REDIS_TRENDING_KEY)
        # Add new scores using ZADD {score1 member1 score2 member2 ...}
        # Note: ZADD expects score first, then member
        members_scores = {item[0]: item[1] for item in trending_data}
        pipe.zadd(config.REDIS_TRENDING_KEY, members_scores)

        # Optional: Trim the sorted set if it grows too large (beyond TOP_N, though ranking already does this)
        # pipe.zremrangebyrank(config.REDIS_TRENDING_KEY, 0, -config.TOP_N - 1)

        results = pipe.execute()
        logger.info(f"Updated Redis sorted set '{config.REDIS_TRENDING_KEY}' with {len(trending_data)} items. Pipeline results: {results}")

    except Exception as e:
        logger.error(f"Error updating Redis: {e}", exc_info=True)

# Example of how this function might be called in Spark (using foreachBatch)
# streaming_query.writeStream \
#     .foreachBatch(lambda df, epoch_id: update_trending_wallpapers(df)) \
#     .start() 