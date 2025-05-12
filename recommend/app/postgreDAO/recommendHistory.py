from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import psycopg2
from psycopg2.extras import RealDictCursor, register_uuid
import uuid
from datetime import datetime
from psycopg2 import sql
import numpy as np
from typing import List, Optional
from contextlib import contextmanager
import logging
import ast
import app.config.databaseConfig as DBConfig

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_CONFIG = DBConfig.POSTGRESQL_CONFIG

register_uuid()

@contextmanager
def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

@contextmanager
def get_db_cursor(commit=False):
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
            if commit:
                conn.commit()
        finally:
            cursor.close()
async def insert_history(user_id, wallpaper_id):
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
        INSERT INTO recommend_history 
        (user_id, wallpaper_id, recommendAt)
        VALUES (%s, %s, %s)
        """,
            (
                user_id,
                wallpaper_id,
                datetime.now()
            )
        )

