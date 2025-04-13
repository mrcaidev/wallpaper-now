# Trending Wallpaper Analyzer

This service analyzes real-time user interaction data from Kafka using Spark Streaming to calculate and store the currently trending wallpapers in Redis.

## Features

- Consumes interaction data from a Kafka topic.
- Uses Spark Streaming with a sliding window to aggregate interaction scores.
- Calculates trending wallpapers based on interaction scores (e.g., likes, downloads).
- Stores the top N trending wallpapers in Redis (using a Sorted Set).

## Prerequisites

- Python 3.8+
- Apache Spark (compatible with PySpark version in `requirements.txt`)
- Kafka Cluster
- Redis Server

## Setup

1.  **Clone the repository** (if applicable)
2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv .venv
    source .venv/bin/activate # On Windows use `.venv\Scripts\activate`
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure environment variables**:
    - Copy `.env.example` to `.env`
    - Fill in the required values in `.env` (Kafka brokers, topic, Spark master, Redis details).

## Running the Analyzer

```bash
# Ensure your Spark environment is correctly set up (e.g., SPARK_HOME)
python src/main.py
```

Or, if using `spark-submit`:

```bash
# Package your application if necessary (e.g., into a zip file)
# spark-submit --master <your_spark_master> --packages org.apache.spark:spark-sql-kafka-0-10_2.12:<spark_version> src/main.py
```

## Docker (Recommended)

A `Dockerfile` is provided for containerization.

1.  **Build the image**:
    ```bash
    docker build -t trending-analyzer .
    ```
2.  **Run the container** (ensure Kafka, Redis are accessible):
    ```bash
    docker run --rm --env-file .env trending-analyzer
    ```

## Configuration

See `.env.example` for configurable parameters like Kafka details, Spark settings (window duration, slide duration, top N), and Redis connection info. 