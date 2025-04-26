import os  # 导入操作系统接口模块
from dotenv import load_dotenv

load_dotenv()

POSTGRESQL_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB", "recommender"),
    "user": os.getenv("POSTGRES_USER", "recommender"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST", "recommender-postgres"),
    "port": os.getenv("POSTGRES_PORT", "5432")
}
vector_dimensions = 512
