import psycopg2
from psycopg2.extras import RealDictCursor, register_uuid
import uuid
from datetime import datetime
import numpy as np
from typing import List, Optional
from contextlib import contextmanager
import logging
import app.config.databaseConfig as DBConfig

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_CONFIG = DBConfig.POSTGRESQL_CONFIG

# 注册UUID类型适配器
register_uuid()

dimensions = DBConfig.vector_dimensions

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

def normalize_vector(vector):
    
    vector_np = np.array(vector)
    norm = np.linalg.norm(vector_np)
    if norm > 0:
        return (vector_np / norm).tolist()
    return vector

def vector_to_pg_format(vector):
    return f"[{','.join(str(x) for x in vector)}]"
    
def create_wallpaper(wallpaper_id, wallpaper_embedding):
    with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                """
            INSERT INTO wallpaper_embedding 
            (wallpaper_id, embedding, norm_embedding, created_at)
            VALUES (%s, %s, %s, %s)
            """,
            (
                    wallpaper_id,
                    vector_to_pg_format(wallpaper_embedding),
                    vector_to_pg_format(normalize_vector(wallpaper_embedding)),
                    datetime.now()
            )
        )
async def get_wallpaper(wallpaper_id):
    with get_db_cursor(commit=True) as cursor:
        try:
            cursor.execute(
            """
                SELECT * FROM wallpaper_embedding 
                WHERE wallpaper_id = %s
            """,
            (
                wallpaper_id,
            )
            )
            
            return cursor.fetchone()
        except Exception as e:
            raise e

def search_similar(user_profiles_norm_vector, limit=10):
    with get_db_cursor(commit=True) as cursor:
            cursor.execute(
        """
        SELECT 
            wallpaper_id,
            ROUND( ( (norm_embedding <#> %s :: vector) * -1 )::numeric, 4 ) AS similarity
        FROM wallpaper_embedding
        ORDER BY similarity DESC
        LIMIT %s
        """,
            (
                    user_profiles_norm_vector,
                    limit
            )
        )
            return cursor.fetchall()
