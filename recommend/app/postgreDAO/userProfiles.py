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

class VectorData(BaseModel):
    values: List[float]

class UserProfileCreate(BaseModel):
    user_id: Optional[uuid.UUID] = None

class UserProfileResponse(BaseModel):
    user_id: uuid.UUID
    preference_vector: List[float]
    norm_preference_vector: List[float]
    last_updated: datetime


def normalize_vector(vector):
    """归一化向量"""
    vector_np = np.array(vector)
    norm = np.linalg.norm(vector_np)
    if norm > 0:
        return (vector_np / norm).tolist()
    return vector

# 辅助函数：向量转换为PostgreSQL向量格式
def vector_to_pg_format(vector):

    return f"[{','.join(str(x) for x in vector)}]"

def generate_user_default_embedding():
    """生成用户默认嵌入向量"""
    # 生成一个默认向量
    return [0.0001] * dimensions

def calculate_new_vector(user_embedding, wallpaper_embedding, weight):
    result_vector = np.multiply(1-weight, ast.literal_eval(user_embedding)) + np.multiply(weight, ast.literal_eval(wallpaper_embedding))
    result_vec = result_vector / np.linalg.norm(ast.literal_eval(user_embedding))
    return result_vec

def insert_default_user_profile(user_id):
    # 初始化向量
    pref_vector = generate_user_default_embedding()
    # 归一化向量
    norm_vector = normalize_vector(pref_vector)
    # 检查是否已存在
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT user_id FROM user_profiles WHERE user_id = %s",
            (user_id,)
        )
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail=f"user ID: {user_id} profiles already exist ")
    
    # 插入数据
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO user_profiles (user_id, preference_vector, norm_preference_vector, last_updated)
            VALUES (%s, %s::vector(%s), %s::vector(%s), %s)
            RETURNING user_id, preference_vector, norm_preference_vector, last_updated
            """,
            (
                user_id,
                vector_to_pg_format(pref_vector),
                dimensions,
                vector_to_pg_format(norm_vector),
                dimensions,
                datetime.now()
            )
        )
        result = cursor.fetchone()
    
    # 处理结果
    if not result:
        raise HTTPException(status_code=500, detail="created User Profiles failed")
    
    # 将PostgreSQL向量类型转换为Python列表
    preference_vector = list(result['preference_vector'])
    norm_preference_vector = list(result['norm_preference_vector'])
    
    return {
        "user_id": result['user_id'],
        "preference_vector": preference_vector,
        "norm_preference_vector": norm_preference_vector,
        "last_updated": result['last_updated']
    }

async def get_user_profile(user_id):
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT user_id, preference_vector, norm_preference_vector, last_updated
            FROM user_profiles
            WHERE user_id = %s
            """,
            (user_id,)
        )
        result = cursor.fetchone()
        
    if not result:
        raise HTTPException(status_code=404, detail=f"userID: {user_id} profiles not found")
    
    # 将PostgreSQL向量类型转换为Python列表
    preference_vector = result['preference_vector']
    norm_preference_vector = result['norm_preference_vector']
    
    return {
        "user_id": result['user_id'],
        "preference_vector": preference_vector,
        "norm_preference_vector": norm_preference_vector,
        "last_updated": result['last_updated']
    }

async def update_user_preference(
    user_id: str,
    user_embedding,
    wallpaper_embedding,
    weight: float
) -> None:
    new_user_embedding = calculate_new_vector(user_embedding, wallpaper_embedding, weight)
    try:       
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
            """
            UPDATE user_profiles
            SET
                preference_vector = %s,
                norm_preference_vector = %s,
                last_updated = NOW()
            WHERE user_id = %s
            """,
            (
                vector_to_pg_format(new_user_embedding), 
                vector_to_pg_format(normalize_vector(new_user_embedding)), 
                user_id
            )
        )          
            
            
    except psycopg2.DatabaseError as e:
        raise RuntimeError(f"Database operation failed: {str(e)}") from e
    except Exception as e:
        raise RuntimeError(f"Unknown Error: {str(e)}") from e
  