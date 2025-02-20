# yz-plugins

元站CMS平台辅助工具

## 环境要求

- python3.6+

## 清理无效网盘链接资源

### 功能说明

清理元站CMS平台的无效网盘链接资源，**目前仅支持夸克链接**。

支持按照以下条件筛选要检测的元站CMS网盘资源：

- 资源分类
- 资源创建时间
- 近期创建资源
- 资源来源：自有资源、订阅资源
- 分页

> **声明**：该功能存在一定风险性，在清理之前需要进行小规模测试，避免损失。

### 使用方法

1. 修改配置文件 `config.json`

```python
{
    "mongodb": {
        # 元站CMS平台mongodb数据库连接信息
        "username": "root",
        "password": "123456",
        "host": "127.0.0.1",
        "port": 27017,
        "db_name": "yz_cms_db"
    },
    # quark网盘cookies（不涉及个人网盘操作，配置未登录状态下的cookies即可，避免请求频繁被封号）
    "quark_cookies": ""
}
```

2. 修改 `code/clean_unvalid_resources.py` 文件，设置筛选条件。

```python
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
```

3. 启动程序：

```bash
python3 clean_unvalid_resources.py
```

4. 处理结果可以通过日志文件 `data_processing.log` 查看。示例：

```bash
2025-01-22 23:18:15,602 - INFO - query: {'created_at': {'$gte': 1732982400, '$lte': 1735574400}, 'source': 4}
2025-01-22 23:18:42,868 - INFO - Deleting item: {'_id': ObjectId('67712c15e8b5ece77494daea'), 'title': '风中的火焰 (2024) 更新10 1080p/4K', 'category': '网络资源', 'category_tags': [], 'content': '<p>名称：风中的火焰 (2024) 更新10 1080p/4K 【蒋奇明/杨采钰/悬疑】<br /><br />描述：2004年宁夏某矿区小镇面临动迁，一具被焚烧的女尸出现在警局门前，死状和10年前当地发生的一起恶性未结案件极为相似，即将退休老刑警褚志强和因工作过失被下调到矿区刑侦队的张韬成为同事，合力侦破案件，在小镇动迁的同时也揭开了过往留下的悲剧真相 。<br /><br />链接<a href="https://pan.quark.cn/s/16a839931f30" rel="noopener" target="_blank">https://pan.quark.cn/s/16a839931f30</a><br /><br /><span class="emoji">📁</span> 大小：NG<br /><span class="emoji">🏷</span> 标签：<a href="https://t.me/yunpanshare/120119?q=%23%E7%8E%8B%E6%99%AF%E6%98%A5">#王景春</a> <a href="https://t.me/yunpanshare/120119?q=%23%E8%92%8B%E5%A5%87%E6%98%8E">#蒋奇明</a> <a href="https://t.me/yunpanshare/120119?q=%23%E6%9D%A8%E9%87%87%E9%92%B0">#杨采钰</a> <a href="https://t.me/yunpanshare/120119?q=%23%E5%89%A7%E6%83%85">#剧情</a> <a href="https://t.me/yunpanshare/120119?q=%23%E6%82%AC%E7%96%91">#悬疑</a> <a href="https://t.me/yunpanshare/120119?q=%23%E7%8A%AF%E7%BD%AA">#犯罪</a> <a href="https://t.me/yunpanshare/120119?q=%23%E9%A3%8E%E4%B8%AD%E7%9A%84%E7%81%AB%E7%84%B0">#风中的火焰</a> <a href="https://t.me/yunpanshare/120119?q=%23quark">#quark</a><br /><span class="emoji">📢</span> 频道：<a href="https://t.me/yunpanshare" target="_blank">@yunpanshare</a><br /><span class="emoji">👥</span> 群组：<a href="https://t.me/yunpangroup" target="_blank">@yunpangroup</a></p><img height="600" src="https://cdn1.cdn-telegram.org/file/VFbtlNF2-yHlr426KGBnm80fKvJjIS7B73iedCMN02CmdG2kGNr0znPuHslahkBZMqJwxtqC31qIzfggHKOedBAiXrG5bQBtkIi8oIp9YRZVQEbqy_s0zL3Iu87FrNcqR5Ud40g2MSf_FOUwuNC044zXiGAgd7au28dr3RG_shvN4iIQh8oIdVa1glUEb0xvj9GjEqvrPMh8r_vhbHTwP01Y1aUJeE_DEJc2RrH5qxmCDaBzufzNo4CqqmPvx5_1ab2tHqG1Phs7NcjTzTf94rzWUcTxqo9Aw21ywuUfLgGR1rdBXkXjJMTZo2oT91Xr-LcAaFDfHVSPJX3KA-ufyg.jpg" width="450" />', 'created_at': 1735470100, 'description': '2004年宁夏某矿区小镇面临动迁，一具被焚烧的女尸出现在警局门前，死状和10年前当地发生的一起恶性未结案件极为相似，即将退休老刑警褚志强和因工作过失被下调到矿区刑侦队的张韬成为同事，合力侦破案件，在小镇动迁的同时也揭开了过往留下的悲剧真相。', 'doc_id': '572ic4jmu7', 'seo_title': 'feng-zhong-de-huo-yan-2024-geng-xin-101080p4K', 'source': 4, 'target_urls': [{'target_name': '夸克', 'target_url': 'https://pan.quark.cn/s/16a839931f30', 'target_mark': ''}], 'updated_at': 1735470100}
2025-01-22 23:18:42,873 - INFO - Deleting item: {'_id': ObjectId('67712be7e8b5ece77494da80'), 'title': '神道帝尊 (2024) 1080P 高码率 无 B 站水印 更新 EP25', 'category': '网络资源', 'category_tags': [], 'content': '<p>名称：神道帝尊 (2024) 1080P 高码率 无 B 站水印 更新 EP25<br />.<br />描述：少年秦阳资质斐然，拥有令人艳羡的修炼神器“星门”，奈何这份幸运却在一夕间被人夺走。濒死时，秦阳体内尘封至宝“封神珠”开启，自此恢复前九世记忆，获得新生。同时，家族陷入前所未有的危机，面对重重考验，秦阳独当一面，凭借前九世积攒的经验和阅历，一次次突破困境。岂料，阴谋家们依然步步紧逼，为了守护珍视之人，秦阳选择抗争到底。<br />.<br />链接：<a href="https://pan.quark.cn/s/536b66a4b60f" rel="noopener" target="_blank">https://pan.quark.cn/s/536b66a4b60f</a><br />.<br /><span class="emoji">📁</span> 大小：X<br /><span class="emoji">🏷</span> 标签：<a href="https://t.me/XiangxiuNB/50048?q=%23%E7%A5%9E%E9%81%93%E5%B8%9D%E5%B0%8A">#神道帝尊</a> <a href="https://t.me/XiangxiuNB/50048?q=%231080P">#1080P</a> <a href="https://t.me/XiangxiuNB/50048?q=%23%E5%8A%A8%E4%BD%9C">#动作</a> <a href="https://t.me/XiangxiuNB/50048?q=%23%E5%A5%87%E5%B9%BB">#奇幻</a> <a href="https://t.me/XiangxiuNB/50048?q=%23%E5%9B%BD%E6%BC%AB">#国漫</a><br /><br /><i>via</i> 匿名</p><img height="761.33" src="https://cdn5.cdn-telegram.org/file/JU5ZxIbBjbgyRloZAYMg0RiP7H0AVan9v0PRgMrnTH_IyIvw6epRWGpWvtkWaqlQl4Hw2YMC3yWZWPgdRXTWHktSoXYZSnFtoGj92AV4BPfQdCFwLYHHpfcUBwj3uRAf_cekAw2ysiKZirMEqUXdNREmd8M1jr3OCtLKfiI7ZRnxn3la3uU5WQ-8OoqYwYfivSl0jjlRmOZEUWDvmz41oBj-8cmM8p6Ljw3RIWnYoeWP_Y-GpgsQz-GBQgU_SIRNTwekNr6LjE281nwEqZouetAt49kzFS-VUuyz9sC7jfkruLDXvGYmTvV1Vi5s83B-fbXU2NoIbs6g3NYmfenwFA.jpg" width="571" />', 'created_at': 1735470055, 'description': '少年秦阳资质斐然，拥有令人艳羡的修炼神器“星门”，奈何这份幸运却在一夕间被人夺走。濒死时，秦阳体内尘封至宝“封神珠”开启，自此恢复前九世记忆，获得新生。同时，家族陷入前所未有的危机，面对重重考验，秦阳独当一面，凭借前九世积攒的经验和阅历，一次次突破困境。岂料，阴谋家们依然步步紧逼，为了守护珍视之人，秦阳选择抗争到底。', 'doc_id': 'ua0ug8jaw7', 'seo_title': 'shen-dao-di-zun-20241080P-gao-ma-lv-wu-B-zhan-shui-yin-geng-xin-EP25', 'source': 4, 'target_urls': [{'target_name': '夸克', 'target_url': 'https://pan.quark.cn/s/536b66a4b60f', 'target_mark': ''}], 'updated_at': 1735470055}
2025-01-22 23:18:42,874 - INFO - Deleting item: {'_id': ObjectId('67712c15e8b5ece77494dae8'), 'title': '清明上河图密码', 'category': '网络资源', 'category_tags': [], 'content': '<p>名称：清明上河图密码 (2024) 4K 26集全 已完结<br /><br />描述：该剧改编自冶文彪的同名小说。宋朝年间，东京城雀儿巷一角生活着赵不尤（张颂文 饰）、温悦（白百何 饰）等性格迥异的一家五口人。赵不尤本是大理寺最底层的贴书小吏，只想过平凡的烟火日子，妻子温悦却一心只想置宅购田，一家人时常吵吵闹闹却也其乐融融。一次意外，一家人被卷入轰动的梅船大案中，开启 了一边破解各类悬案、一边解决层出不穷的家庭问题的奇妙之旅。在此过程中，一家人重新认识并接纳了彼此，也各自收获了成长，携手渡过重重难关。随着一桩桩案件破解，一切线索都指向了“江南大善人”。最终通过一家五口的共同努力揭露了恶人的伪善与恶行，打破了行市垄断、仕途不明的混沌局面，既捍卫了小家的幸福，也守护了东京城百姓的安乐。<br /><br />链接：<a href="https://pan.quark.cn/s/f02e7bde0889" rel="noopener" target="_blank">https://pan.quark.cn/s/f02e7bde0889</a><br /><br /><span class="emoji">📁</span> 大小：X<br /><span class="emoji">🏷</span> 标签：<a href="https://t.me/yunpanshare/120122?q=%23%E6%B8%85%E6%98%8E%E4%B8%8A%E6%B2%B3%E5%9B%BE%E5%AF%86%E7%A0%81">#清明上河图密码</a> <a href="https://t.me/yunpanshare/120122?q=%234K">#4K</a> <a href="https://t.me/yunpanshare/120122?q=%23%E6%82%AC%E7%96%91">#悬疑</a> <a href="https://t.me/yunpanshare/120122?q=%23%E5%8F%A4%E8%A3%85">#古装</a> <a href="https://t.me/yunpanshare/120122?q=%23%E5%BC%A0%E9%A2%82%E6%96%87">#张颂文</a> <a href="https://t.me/yunpanshare/120122?q=%23%E7%99%BD%E7%99%BE%E5%90%88">#白百合</a> <a href="https://t.me/yunpanshare/120122?q=%23quark">#quark</a><br /><span class="emoji">📢</span> 频道：<a href="https://t.me/yunpanshare" target="_blank">@yunpanshare</a><br /><span class="emoji">👥</span> 群组：<a href="https://t.me/yunpangroup" target="_blank">@yunpangroup</a></p><img height="600" src="https://cdn5.cdn-telegram.org/file/tbsn2SOHoKpPRQM2nXD4DGXPc9mD-eRlMFF6xrIi22IOneOTkdmg2cSNiQXP9PZJWJWv6sL5dqvi6ZnqS0buZ1afHezb-uPvocEbcAP3tFCINaVGbLgQ3R19HjJQXMZTGd27PTzZGTzp4uwGmaG-xs6L4Wk9qxD6P-_LFhh3RSlYe7aF1xZ-WBJRHzyv7opWmFcbMD0CsnidfMkubCK9_WOTH4a_QqlmF-FBvybKRqDJTfn_AHt-AMWfK8SbODMZKSvysgLl47CbvcY1shy9yoSQv-xNL6FFI5QK2to451HgbgJYSdVJzFfXOvBPg4PoR_1RW9v2Tg5-cImCYJTW9A.jpg" width="450" />', 'created_at': 1735470100, 'description': '该剧改编自冶文彪的同名小说。宋朝年间，东京城雀儿巷一角生活着赵不尤（张颂文 饰）、温悦（白百何 饰）等性格迥异的一家五口人。赵不尤本是大理寺最底层的贴书小吏，只想过平凡的烟火日子，妻子温悦却一心只想置宅购田，一家人时常吵吵闹闹却也其乐融融。一次意外，一家人被卷入轰动的梅船大案中，开启了一边破解各类悬案、一边解决层出不穷的家庭问题的奇妙之旅。在此过程中，一家人重新认识并接纳了彼此，也各自收获了成长，携手渡过重重难关。随着一桩桩案件破解，一切线索都指向了“江南大善人”。最终通过一家五口的共同努力揭露了恶人的伪善与恶行，打破了行市垄断、仕途不明的混沌局面，既捍卫了小家的幸福，也守护了东京城百姓的安乐。', 'doc_id': 'babb4r3l3z', 'seo_title': 'qing-ming-shang-he-tu-mi-ma', 'source': 4, 'target_urls': [{'target_name': '夸克', 'target_url': 'https://pan.quark.cn/s/f02e7bde0889', 'target_mark': ''}], 'updated_at': 1735470100}
2025-01-22 23:18:43,095 - INFO - Deleting item: {'_id': ObjectId('67712be7e8b5ece77494da89'), 'title': '清明上河图密码 (2024) 4K 26集全 已完结', 'category': '网络资源', 'category_tags': [], 'content': '<p>名称：清明上河图密码 (2024) 4K 26集全 已完结<br />.<br />描述：该剧改编自冶文彪的同名小说。宋朝年间，东京城雀儿巷一角生活着赵不尤（张颂文 饰）、温悦（白百何 饰）等性格迥异的一家五口人。赵不尤本是大理寺最底层的贴书小吏，只想过平凡的烟火日子，妻子温悦却一心只想置宅购田，一家人时常吵吵闹闹却也其乐融融。一次意外，一家人被卷入轰动的梅船大案中，开启 了一边破解各类悬案、一边解决层出不穷的家庭问题的奇妙之旅。在此过程中，一家人重新认识并接纳了彼此，也各自收获了成长，携手渡过重重难关。随着一桩桩案件破解，一切线索都指向了“江南大善人”。最终通过一家五口的共同努力揭露了恶人的伪善与恶行，打破了行市垄断、仕途不明的混沌局面，既捍卫了小家的幸福，也守护了东京城百姓的安乐。<br />.<br />链接：<a href="https://pan.quark.cn/s/f02e7bde0889" rel="noopener" target="_blank">https://pan.quark.cn/s/f02e7bde0889</a><br />.<br /><span class="emoji">📁</span> 大小：X<br /><span class="emoji">🏷</span> 标签：<a href="https://t.me/XiangxiuNB/50036?q=%23%E6%B8%85%E6%98%8E%E4%B8%8A%E6%B2%B3%E5%9B%BE%E5%AF%86%E7%A0%81">#清明上河图密码</a> <a href="https://t.me/XiangxiuNB/50036?q=%234K">#4K</a> <a href="https://t.me/XiangxiuNB/50036?q=%23%E6%82%AC%E7%96%91">#悬疑</a> <a href="https://t.me/XiangxiuNB/50036?q=%23%E5%8F%A4%E8%A3%85">#古装</a> <a href="https://t.me/XiangxiuNB/50036?q=%23%E5%BC%A0%E9%A2%82%E6%96%87">#张颂文</a> <a href="https://t.me/XiangxiuNB/50036?q=%23%E7%99%BD%E7%99%BE%E5%90%88">#白百合</a><br /><br /><i>via</i> 匿名</p><img height="600" src="https://cdn5.cdn-telegram.org/file/vePsHxmn4fmKfeBWHmoK35s11g16eK3EAErY7KpjRyqRyc2hBmUSq09rSX4OC5LUWcqfUL3ot1Nj3AMykxu7tISvRTztnez34ft2r5e_o_6ymDEXDYVo--gH8SMwXb-xxkNJLliUdSaQ2kFy8LpvLtCCARTJwGx58UNMXGq5aGrdxeeYrjDfMK2-wSNyPpOcBMkXemkPy0_Nr8QTZ1VAJLrVJqAEX_A9LiL-9_zALMkL4edVlDlL24H6pDqqId5w1DFMQSaZvOoJveMNq6MaS1aCIG-vHtPyAJuFN6fITn-2USUYg7JD8CylPiznFJiTWO1AfXgbOpHCkSXcGQEwjw.jpg" width="450" />', 'created_at': 1735470055, 'description': '该剧改编自冶文彪的同名小说。宋朝年间，东京城雀儿巷一角生活着赵不尤（张颂文 饰）、温悦（白百何 饰）等性格迥异的一家五口人。赵不尤本是大理寺最底层的贴书小吏，只想过平凡的烟火日子，妻子温悦却一心只想置宅购田，一家人时常吵吵闹闹却也其乐融融。一次意外，一家人被卷入轰动的梅船大案中，开启了一边破解各类悬案、一边解决层出不穷的家庭问题的奇妙之旅。在此过程中，一家人重新认识并接纳了彼此，也各自收获了成长，携手渡过重重难关。随着一桩桩案件破解，一切线索都指向了“江南大善人”。最终通过一家五口的共同努力揭露了恶人的伪善与恶行，打破了行市垄断、仕途不明的混沌局面，既捍卫了小家的幸福，也守护了东京城百姓的安乐。', 'doc_id': 'wg78pcd5dk', 'seo_title': 'qing-ming-shang-he-tu-mi-ma-20244K26-ji-quan-yi-wan-jie', 'source': 4, 'target_urls': [{'target_name': '夸克', 'target_url': 'https://pan.quark.cn/s/f02e7bde0889', 'target_mark': ''}], 'updated_at': 1735470055}
2025-01-22 23:18:43,097 - INFO - update item: {'_id': ObjectId('67712be7e8b5ece77494da8d'), 'title': '风中的火焰（2024）4K EDR 高码率 更至 EP10', 'category': '网络资源', 'category_tags': [], 'content': '<p><b>名称：风中的火焰（2024）4K EDR 高码率 更至 EP10</b><br />ㅤ<br />描述：2004 年宁夏某矿区小镇面临动迁，一具被焚烧的女尸出现在警局门前，死状和 10 年前当地发生的一起恶性未结案件极为相似，即将退休老刑警褚志强和因工作过失被下调到矿区刑侦队的张韬成为同事，合力侦破案件，在小镇动迁的同时也揭开了过往留下的悲剧真相 。<br />ㅤ<br />夸克：<a href="https://pan.quark.cn/s/a9a9d0843b45" rel="noopener" target="_blank">https://pan.quark.cn/s/a9a9d0843b45</a><br />移动：<a href="https://caiyun.139.com/m/i?2jexCziEXdp53" rel="noopener" target="_blank">https://caiyun.139.com/m/i?2jexCziEXdp53</a><br />百度：<a href="https://pan.baidu.com/s/1_DgmctdXMfy_QwBHCWaQqA?pwd=vwjt" rel="noopener" target="_blank">https://pan.baidu.com/s/1_DgmctdXMfy_QwBHCWaQqA?pwd=vwjt</a><br />ㅤ<br /><span class="emoji">📁</span> 大小：5G/ 集<br /><span class="emoji">🏷</span> 标签：<a href="https://t.me/XiangxiuNB/50032?q=%23%E9%A3%8E%E4%B8%AD%E7%9A%84%E7%81%AB%E7%84%B0">#风中的火焰</a> <a href="https://t.me/XiangxiuNB/50032?q=%23%E8%92%8B%E5%A5%87%E6%98%8E">#蒋奇明</a> <a href="https://t.me/XiangxiuNB/50032?q=%23%E7%8E%8B%E6%99%AF%E6%98%A5">#王景春</a> <a href="https://t.me/XiangxiuNB/50032?q=%23%E5%89%A7%E6%83%85">#剧情</a> <a href="https://t.me/XiangxiuNB/50032?q=%23%E6%82%AC%E7%96%91">#悬疑</a> <a href="https://t.me/XiangxiuNB/50032?q=%23%E7%8A%AF%E7%BD%AA">#犯罪</a><br /><br /><i>via</i> 匿名</p><img height="600" src="https://cdn5.cdn-telegram.org/file/J4MxwU5Q4RfbWKfCtpSielGkWN6x9Dv1jETg-LN2TjkCHOzcDGCyj_s2Yxs0CG9vRfkpshYBfAqUn1TvcYSCuWHeZ_zoZmBU9dwysujCUIKIfBGZO7I4PN2iFZ87UXOQlsxP0p-pNHLgBDczRNX0H_YBpFDUljnlnGZSqFCcbNnemTWhHixw3msCzXAWc7W5FwW0llzMzkALhrzqc6XXP3ccTQmupLxPZHlxGhAP25AQJmirDw0BNyphOWAhYBOUVlafov-SPk3lZKk2JR-mEvQ-k_MnmESicOHQ0Fk_4deQMAWxu15OdKT3iCP2DmvR49M6ecZvzGfHf3I1cvh9ag.jpg" width="450" />', 'created_at': 1735470055, 'description': '2004 年宁夏某矿区小镇面临动迁，一具被焚烧的女尸出现在警局门前，死状和 10 年前当地发生的一起恶性未结案件极为相似，即将退休老刑警褚志强和因工作过失被下调到矿区刑侦队的张韬成为同事，合力侦破案件，在小镇动迁的同时也揭开了过往留下的悲剧真相 。', 'doc_id': 'wed3l6f0q1', 'seo_title': 'feng-zhong-de-huo-yan-20244KEDR-gao-ma-lv-geng-zhi-EP10', 'source': 4, 'target_urls': [{'target_name': '夸克', 'target_url': 'https://pan.quark.cn/s/a9a9d0843b45', 'target_mark': ''}, {'target_name': '百度', 'target_url': 'https://pan.baidu.com/s/1_DgmctdXMfy_QwBHCWaQqA?pwd=vwjt', 'target_mark': ''}], 'updated_at': 1735470055}
```
