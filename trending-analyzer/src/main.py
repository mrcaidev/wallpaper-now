import logging  # 导入日志模块
import sys  # 导入系统模块，用于退出程序
from spark_processor import get_spark_session, process_stream  # 从spark_processor模块导入函数

# 配置日志记录
logging.basicConfig(  # 基本日志配置
    level=logging.INFO,  # 设置日志级别为 INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 设置日志格式
    handlers=[  # 设置日志处理器
        logging.StreamHandler(sys.stdout)  # 将日志输出到标准输出
    ]
)

logger = logging.getLogger(__name__)  # 获取当前模块的 logger 实例

def main():  # 定义主函数
    logger.info("启动趋势壁纸分析器...")
    spark = None  # 初始化 spark 变量为 None
    try:  # 开始异常处理块
        # 获取 Spark Session
        spark = get_spark_session()  # 调用函数获取 SparkSession

        # 开始处理流数据
        process_stream(spark)  # 调用函数开始处理数据流，传入 SparkSession

    except Exception as e:  # 捕获所有异常
        logger.critical(f"发生意外错误: {e}", exc_info=True) # 记录严重错误信息及堆栈
        sys.exit(1)  # 程序异常退出，返回状态码 1
    finally:  # 定义 finally 块，无论是否发生异常都会执行
        if spark:  # 检查 spark 变量是否已成功赋值
            logger.info("停止 SparkSession...")
            spark.stop()  # 停止 SparkSession
            logger.info("SparkSession 已停止。")
        logger.info("趋势壁纸分析器已结束。")

if __name__ == "__main__":  # 判断是否作为主脚本运行
    main()  # 调用主函数 