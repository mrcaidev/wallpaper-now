#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from src.spark_processor import get_spark_session, process_stream  # 从spark_processor模块导入函数

import logging
import os
import time
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("启动趋势壁纸分析器...")
    try:
        logger.info("正在初始化SparkSession...")
        spark = get_spark_session()  # 调用函数获取 SparkSession
        logger.info("SparkSession初始化成功，准备处理流数据...")
        # 处理流数据
        process_stream(spark)
    except Exception as e:
        logger.critical(f"发生意外错误: {e}")
        # 输出更详细的异常信息，便于诊断
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")
    
    logger.info("趋势壁纸分析器已结束。")

if __name__ == "__main__":
    main() 