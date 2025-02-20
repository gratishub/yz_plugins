import random
import time
import pymongo
import logging
import datetime
import json
import pprint
from quark import Quark
from concurrent.futures import ThreadPoolExecutor


def read_config():
    with open('config.json', 'r') as f:
        config = json.load(f)
    return config

config = read_config()
quark_cookies = config.get("quark_cookies", "")
quark = Quark(quark_cookies, 0)

def check_valid(target_url):
    # 返回 True 表示链接有效，False 表示无效
    if not target_url:
        return False
    if target_url.startswith('https://pan.quark.cn'):
        pwd_id, passcode, pdir_fid = quark.get_id_from_url(target_url)
        # 获取stoken，同时可验证资源是否失效
        is_sharing, stoken = quark.get_stoken_with_retry(pwd_id, passcode)
        return is_sharing
    else:
        return True


def setup_logger():
    logger = logging.getLogger('data_processing')
    logger.setLevel(logging.INFO)
    # 创建文件处理器
    file_handler = logging.FileHandler('data_processing.log', encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


def build_query(category=None, created_at_start=None, created_at_end=None, recent=None, source=None):
    query = {}
    if category:
        query["category"] = category
    if created_at_start and created_at_end:
        # 将 datetime 转换为时间戳
        query["created_at"] = {"$gte": int(created_at_start.timestamp()), "$lte": int(created_at_end.timestamp())}
    elif created_at_start:
        query["created_at"] = {"$gte": int(created_at_start.timestamp())}
    elif created_at_end:
        query["created_at"] = {"$lte": int(created_at_end.timestamp())}
    elif recent:
        now = datetime.datetime.now()
        if recent.endswith('month'):
            delta = datetime.timedelta(days=30 * int(recent[:-5]))
        elif recent.endswith('day'):
            delta = datetime.timedelta(days=int(recent[:-3]))
        elif recent.endswith('hour'):
            delta = datetime.timedelta(hours=int(recent[:-4]))
        else:
            raise ValueError("Invalid recent format. Use 'xx month/day/hour'.")
        # 将时间范围转换为时间戳
        query["created_at"] = {"$gte": int((now - delta).timestamp())}
    if source is not None:
        query["source"] = source
    return query


def main():
    # 读取配置文件
    mongo_config = config.get("mongodb", {})
    username = mongo_config.get("username")
    password = mongo_config.get("password")
    host = mongo_config.get("host", "localhost")
    port = mongo_config.get("port", 27017)
    db_name = mongo_config.get("db_name", "yz_cms_db")
    logger = setup_logger()

    # 连接 MongoDB 数据库
    client = pymongo.MongoClient(
        f"mongodb://{username}:{password}@{host}:{port}/?authSource=admin"
    )
    db = client[db_name]
    collection = db["d_site_resource"]
    last_id = None  # 记录上一次查询的最后一个元素的 _id
    
    def process_item(item):
        target_urls = item.get("target_urls", [])
        original_length = len(target_urls)
        new_target_urls = []
        for target_url_obj in target_urls:
            target_url = target_url_obj.get("target_url")
            if check_valid(target_url):
                print(f"title: {item.get('title')} url: {target_url} valid")
                new_target_urls.append(target_url_obj)
            else:
                print(f"title: {item.get('title')} url: {target_url} invalid")
        if len(new_target_urls) == 0:
            # 记录删除操作
            logger.info(f"Deleting item: {item}")
            collection.delete_one({"_id": item["_id"]})
        elif len(new_target_urls) < original_length:
            # 仅在 target_urls 列表长度有变化时更新
            logger.info(f"update item: {item}")
            collection.update_one({"_id": item["_id"]}, {"$set": {"target_urls": new_target_urls}})


    def process_data(category=None, created_at_start=None, created_at_end=None, recent=None, source=None, page_num=1, page_size=100, batch_size=100, print_query=False):
        nonlocal last_id
        query = build_query(category, created_at_start, created_at_end, recent, source)
        # 按照 created_at 字段由近到远排序
        sort_order = [("created_at", pymongo.DESCENDING)]
        batch_count = 0
        while True:        # 分页查询
            if print_query:
                logger.info(f"query: {query}\tpage_num: {page_num}\tpage_size: {page_size}\tlast_id: {last_id}")
            batch_query = query.copy()
            if last_id:
                batch_query["_id"] = {"$gt": last_id}
            cursor = collection.find(batch_query).sort(sort_order).limit(page_size)
            items = []
            for item in cursor:
                last_id = item["_id"]  # 更新 last_id
                items.append(item)
                if len(items) == batch_size:
                    break
            if not items:
                break
            with ThreadPoolExecutor() as executor:
                futures = []
                for item in items:
                    future = executor.submit(process_item, item)
                    futures.append(future)
                for future in futures:
                    future.result()
            batch_count += 1
            if batch_count % 100 == 0:
                # 每 100 个批次随机等待 0 到 1 秒
                wait_time = random.uniform(0, 1)
                time.sleep(wait_time)
            
    # 调用示例，筛选创建时间在 2024 年 1 月 1 日至 2024 年 12 月 31 日的数据
    start_time = datetime.datetime(2024, 12, 31)
    end_time = datetime.datetime(2025, 1, 23)
    # start_time = None
    # end_time = None
    # 筛选 category
    category = "网络资源"
    category = None
    # 筛选最近 1 天的数据
    recent = "10 day"
    recent = None
    # 筛选 source：1-自有资源；4-订阅资源
    source = 4
    page_size = 100  # 每页数据量
    page_num = 1  # 初始页码
    print_query = True
    batch_size = 100  # 每批次的数据量
    process_data(category=category, created_at_start=start_time, created_at_end=end_time, recent=recent, source=source, page_size=page_size, batch_size=batch_size, print_query=True)

if __name__ == "__main__":
    main()
