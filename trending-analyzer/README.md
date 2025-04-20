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

See `.env.example` for configurable parameters like Kafka details, Spark settings (window duration, slide duration, top N), and Redis connection info.

## Running the API server

```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

## API Documentation

### Trending Wallpapers Endpoint

Get a list of currently trending wallpapers sorted by popularity.

- **URL**: `/api/v1/wallpapers/trending`
- **Method**: GET
- **Query Parameters**:
  - `limit` (optional): Number of results to return (default: 10, max: 100)，enter 0 to get all results
  - `offset` (optional): Number of results to skip (default: 0)

#### Response Format

The API returns an ordered array of wallpaper UUIDs, with the most trending wallpapers first:

```json
[
  "123e4567-e89b-12d3-a456-426614174000",
  "7bac9210-5a9d-4911-8d1d-292c44310a3a",
  "9f8e7d6c-5b4a-3c2d-1e0f-9a8b7c6d5e4f",
  "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
  "f1e2d3c4-b5a6-9876-5432-1fedcba98765"
]
```

Each ID is in UUID format (`8-4-4-4-12` hexadecimal digits) and corresponds to a wallpaper in the wallpaper-manager service. 