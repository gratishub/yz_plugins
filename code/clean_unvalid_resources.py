import random
import time
import pymongo
import logging
from logging.handlers import RotatingFileHandler
import datetime
import json
from quark import Quark
from concurrent.futures import ThreadPoolExecutor
from pymongo.monitoring import CommandListener
from typing import Optional, Dict, Any
from pymongo.errors import PyMongoError
from pymongo.collection import Collection

class ConfigValidationError(Exception):
    """配置验证异常"""

class MongoCommandMonitor(CommandListener):
    """MongoDB 命令监听器"""
    
    def __init__(self, logger: logging.Logger):
        super().__init__()
        self.logger = logger if logger else logging.getLogger('MongoCommandMonitor')
        
    def started(self, event):
        self.logger.debug(f"命令开始: {event.command_name} | 命令内容: {event.command}")

    def succeeded(self, event):
        self.logger.debug(f"命令成功: {event.command_name} | 耗时: {event.duration_micros} 微秒")
        

def load_and_validate_config(config_path: str = 'config.json') -> Dict[str, Any]:
    """加载并验证配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise ConfigValidationError(f"配置文件加载失败: {str(e)}")

    # MongoDB 配置校验
    mongo_cfg = config.get('mongodb', {})
    required_mongo_keys = ['username', 'password', 'host', 'port', 'db_name']
    if any(key not in mongo_cfg for key in required_mongo_keys):
        raise ConfigValidationError("MongoDB 配置不完整")

    # 时间范围校验
    processing_cfg = config.get('processing', {})
    time_range = processing_cfg.get('time_range', {})
    if time_range:
        try:
            start = datetime.datetime.fromisoformat(time_range.get('start', ''))
            end = datetime.datetime.fromisoformat(time_range.get('end', ''))
            if start > end:
                raise ValueError("时间范围起始时间不能晚于结束时间")
        except ValueError as e:
            raise ConfigValidationError(f"时间格式错误: {str(e)}")

    # 分页参数校验
    query_batch = mongo_cfg.get('query_batch', {})
    if not all(isinstance(query_batch.get(k), int) for k in ['page_size', 'batch_size']):
        raise ConfigValidationError("分页参数必须为整数")

    return config

def setup_logger(logging_config: Dict[str, Any]) -> logging.Logger:
    """配置带滚动记录的日志记录器"""
    logger = logging.getLogger('data_processing')
    logger.setLevel(logging_config.get('level', 'INFO').upper())
    
    handler = RotatingFileHandler(
        filename=logging_config.get('filename', 'data_processing.log'),
        maxBytes=logging_config.get('max_bytes', 10*1024*1024),
        backupCount=logging_config.get('backup_count', 5),
        encoding='utf-8'
    )
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

class ResourceProcessor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = setup_logger(config.get('logging', {}))
        self.quark = self._init_quark()
        self.mongo_collection = self._init_mongo()
        self.quark_retry_times = self.config.get('quark', {}).get('retry_times', 3)

    def _init_quark(self) -> Quark:
        """初始化夸克客户端"""
        quark_cfg = self.config.get('quark', {})
        return Quark(
            cookie=quark_cfg.get('cookies', ''),
            index=0
        )

    def _init_mongo(self) -> Collection:
        """初始化 MongoDB 连接"""
        mongo_cfg = self.config['mongodb']
        client = pymongo.MongoClient(
            f"mongodb://{mongo_cfg['username']}:{mongo_cfg['password']}"
            f"@{mongo_cfg['host']}:{mongo_cfg['port']}/?authSource=admin",
            event_listeners=[MongoCommandMonitor(self.logger)]
        )
        return client[mongo_cfg['db_name']]['d_site_resource']

    def build_query(self) -> Dict[str, Any]:
        """构建 MongoDB 查询条件"""
        processing_cfg = self.config.get('processing', {})
        query = {}
        
        if category := processing_cfg.get('category'):
            query['category'] = category
            
        if source := processing_cfg.get('source'):
            query['source'] = source
            
        time_range = processing_cfg.get('time_range')
        if time_range:
            start = datetime.datetime.fromisoformat(time_range['start'])
            end = datetime.datetime.fromisoformat(time_range['end'])
            query['created_at'] = {
                '$gte': int(start.timestamp()),
                '$lte': int(end.timestamp())
            }
            
        return query

    def process_batch(self):
        """批量处理数据"""
        mongo_cfg = self.config['mongodb']['query_batch']
        processing_cfg = self.config.get('processing', {})
        
        last_id = None
        total_processed = 0
        query = self.build_query()

        while True:
            try:
                batch_query = query.copy()
                if last_id:
                    batch_query['_id'] = {'$gt': last_id}

                cursor = self.mongo_collection.find(batch_query).sort([('_id', 1)]).limit(mongo_cfg['batch_size'])
                items = list(cursor)

                if not items:
                    self.logger.info(f"处理完成，共处理 {total_processed} 条记录")
                    break

                with ThreadPoolExecutor(max_workers=mongo_cfg.get('max_workers', 4)) as executor:
                    for item in items:
                        executor.submit(self.process_item, item)

                last_id = items[-1]['_id']
                total_processed += len(items)

                if total_processed % mongo_cfg['throttling']['batch_frequency'] == 0:
                    wait = random.uniform(
                        mongo_cfg['throttling']['min_wait'],
                        mongo_cfg['throttling']['max_wait']
                    )
                    time.sleep(wait)

            except PyMongoError as e:
                self.logger.error(f"MongoDB 操作失败: {str(e)}")
                time.sleep(5)  # 错误后等待重试

    def process_item(self, item: Dict[str, Any]):
        """处理单个资源项"""
        valid_urls = []
        for url_obj in item.get('target_urls', []):
            url = url_obj.get('target_url', '')
            if self.is_valid_url(url):
                valid_urls.append(url_obj)
                self.logger.debug(f"有效链接: {url}")
            else:
                self.logger.info(f"无效链接: {url} (资源: {item.get('title')})")

        update_op = {'$set': {'target_urls': valid_urls}} if valid_urls else None
        self.update_mongo_item(item['_id'], update_op)

    def is_valid_url(self, url: str) -> bool:
        """验证 URL 有效性"""
        if not url:
            return False
            
        if url.startswith('https://pan.quark.cn'):
            pwd_id, passcode, _ = self.quark.get_id_from_url(url)
            is_sharing, _ = self.quark.get_stoken_with_retry(pwd_id, passcode, max_retries=self.quark_retry_times)
            return is_sharing
            
        return True  # 其他类型链接默认有效

    def update_mongo_item(self, item_id: Any, update_op: Optional[Dict]):
        """更新 MongoDB 记录"""
        try:
            if update_op:
                self.mongo_collection.update_one({'_id': item_id}, update_op)
                self.logger.debug(f'更新 {item_id}')
            else:
                self.mongo_collection.delete_one({'_id': item_id})
                self.logger.debug(f'删除 {item_id}')
        except PyMongoError as e:
            self.logger.error(f"更新记录失败 (ID: {item_id}): {str(e)}")

def main():
    try:
        config = load_and_validate_config(config_path='config-dev.json')
        processor = ResourceProcessor(config)
        processor.process_batch()
    except (ConfigValidationError, PyMongoError) as e:
        logging.error(f"程序启动失败: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()