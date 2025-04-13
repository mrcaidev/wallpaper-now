# Use an official Python runtime as a parent image
# Choose a version compatible with PySpark and your environment
FROM python:3.9-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies that might be needed by PySpark or other libs
# (Optional, depending on your base image and specific needs)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# Install required Python packages
# Copy only requirements first to leverage Docker cache
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY src/ /app/src/
# Copy .env file - Use with caution! Prefer runtime environment variables.
# If you uncomment this, ensure the .env file exists during the build.
# COPY .env /app/.env

# Command to run the application
# Ensure Spark environment (like SPARK_HOME, Hadoop config) is available
# This might require a custom base image with Spark installed, or mounting Spark binaries
# If Spark is running externally (like a cluster), you might only need PySpark library
CMD ["python", "src/main.py"] 