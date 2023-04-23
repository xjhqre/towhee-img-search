"""
以图搜图配置文件，批量处理
"""
import os

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
save_path = os.path.join(FILE_DIR, 'static', 'uploaded')

# 要提取特征图片库的地址，示例：'F:/ACG/出处归档/*'
train_pic_path = 'F:/ACG/壁纸/*'

types = [".jpg", ".jpeg", ".gif", ".png", ".JPG", ".JPEG", ".GIF", ".PNG"]

# elasticsearch
elasticsearch_index = "imgsearch"  # 索引名，示例 imgsearch
elasticsearch_url = '1.15.88.204'  # elasticsearch的ip
elasticsearch_port = "9201"  # elasticsearch服务的端口，示例：9200


folder = ''  # bucket下的文件夹名，示例：'test/'
pic_oss_url = "" + folder  # oss存储地址前缀，示例："https://{bucket名称}.oss-cn-hangzhou.aliyuncs.com/" + folder
