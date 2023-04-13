import os
import time
import urllib
from glob import glob
from elasticsearch import Elasticsearch
from towhee.dc2 import pipe, ops
import config
import image_decode_custom


'''
提取图片特征向量上传es
'''

cnt = 0  # 图片处理计数
es = Elasticsearch([{'host': config.elasticsearch_url, 'port': config.elasticsearch_port}], timeout=3600)
image_decode_custom = image_decode_custom.ImageDecodeCV2()


# Load image path
def load_image(folderPath):
    for filePath in glob(folderPath):
        if os.path.splitext(filePath)[1] in config.types:
            yield filePath


# 生成对应图片向量，存储到es
def es_insert(filePath, vec):
    vec = vec[::2]  # 特征向量，resnet50提取的图片向量维度是2048，es7.4版本支持的最大维度是1024
    fileName = os.path.basename(filePath)  # 图片名称
    imgUrl = config.pic_oss_url + urllib.parse.quote(fileName)  # OSS地址

    doc = {'url': imgUrl, 'feature': vec,
           'name': fileName}

    es.index(config.elasticsearch_index, body=doc)  # 保存到elasticsearch

    global cnt
    cnt += 1
    print("当前图片：" + imgUrl + " ---> " + str(cnt))

def extract(galleryPath):
    for path in glob(galleryPath):
        if os.path.splitext(path)[1] not in config.types:
            continue
        img = image_decode(path)
        vec = image_embedding(img)
        es_insert(path, vec)

# Embedding pipeline
# p_embed = (
#     pipe.input('src')
#     # 传入src，输出img_path
#     .flat_map('src', 'img_path', load_image)
#     # 传入img_path，输出img
#     .map('img_path', 'img', image_decode_custom)
#     # 传入img，输出vec
#     .map('img', 'vec', ops.image_embedding.timm(model_name='resnet50'))
# )
#
# # Insert pipeline
# p_insert = (
#     # 传入('img_path', 'vec')，无输出
#     p_embed.map(('img_path', 'vec'), (), es_insert)
#     .output()
# )

if __name__ == '__main__':
    start_time = time.time()
    extract(config.train_pic_path)
    # p_insert(config.train_pic_path)
    end_time = time.time()
    total_time = end_time - start_time
    print("程序运行时间为：", total_time, "秒")
