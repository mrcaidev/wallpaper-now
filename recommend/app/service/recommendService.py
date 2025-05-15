from app.postgreDAO.userProfiles import insert_default_user_profile, get_user_profile, update_user_preference
from app.postgreDAO.wallpaperEmbedding import create_wallpaper, search_similar, get_wallpaper,get_random_wallpaper
import logging
import uuid
from app.postgreDAO.recommendHistory import insert_history
import random
from fastapi import HTTPException, status

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_uuid4(user_id: str) -> None:
    try:
        uuid.UUID(user_id, version=4)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format"
        )
    
async def create_user_profile(user_id):
    insert_default_user_profile(user_id)

async def create_wallpaper_embedding(wallpaper_id, wallpaper_embedding):
    create_wallpaper(wallpaper_id, wallpaper_embedding)

async def get_wallpaper_recommendations(user_id):
    validate_uuid4(user_id)
    logger.info("userId: "+user_id)
    try:
        result = await get_user_profile(user_id)
        recommended_wallpapers = search_similar(user_id, result["norm_preference_vector"])
        list_recommendations = random.sample(recommended_wallpapers, 8)
        if list_recommendations and len(list_recommendations) > 0:
            # 创建记录推荐历史的任务列表
            for wallpaper in list_recommendations:
                wallpaper_id = wallpaper.get("wallpaper_id")  # 假设每个壁纸对象中有wallpaper_id字段
                if wallpaper_id:
                    await insert_history(user_id, wallpaper_id)
        list_random = await get_random_wallpaper(2)
        list_recommendations.extend(list_random)
        return list_recommendations
    except Exception as e:
        print(e)
        logger.error("error")

async def get_random_wallpaper_recommend(limit):
    try:
        return await get_random_wallpaper(limit)
    except Exception as e:
        print(e)
        logger.error("error")



async def update_user_profile(user_id, wallpaper_id, weight):
    validate_uuid4(user_id)
    validate_uuid4(wallpaper_id)

    user_profile = await get_user_profile(user_id)
    wallpaper = await get_wallpaper(wallpaper_id)
    await update_user_preference(user_id, user_profile["preference_vector"], wallpaper["embedding"], weight)

async def insert_recommend_history(user_id, wallpaper_id):
    validate_uuid4(user_id)
    await insert_history(user_id, wallpaper_id)
    

    