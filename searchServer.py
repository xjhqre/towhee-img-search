# -*- coding: utf-8 -*-
import os
import urllib
from glob import glob

from PIL import Image
from elasticsearch import Elasticsearch
# -*- coding: utf-8 -*-
import config
from towhee.dc2 import pipe, ops, DataCollection
from flask import Flask, request, render_template
import image_decode_custom

'''
    以图搜图服务
'''

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
es = Elasticsearch([{'host': config.elasticsearch_url, 'port': config.elasticsearch_port}], timeout=3600)
image_decode_custom = image_decode_custom.ImageDecodeCV2()
last_upload_img = ""


# es查询
def feature_search(query):
    global es
    # print(query)
    results = es.search(
        index=config.elasticsearch_index,
        body={
            "size": 30,
            "query": {
                "script_score": {
                    "query": {
                        "match_all": {}
                    },
                    "script": {
                        "source": "cosineSimilarity(params.queryVector, doc['feature'])+1.0",
                        "params": {
                            "queryVector": query[::2]
                        }
                    }
                }
            }
        })
    hitCount = results['hits']['total']['value']

    if hitCount > 0:
        answers = []
        max_score = results['hits']['max_score']

        if max_score >= 0.35:
            for hit in results['hits']['hits']:
                if hit['_score'] > 0.5 * max_score:
                    imgurl = hit['_source']['url']
                    name = hit['_source']['name']
                    imgurl = imgurl.replace("#", "%23")
                    answers.append([imgurl, name])
    else:
        answers = []
    return answers


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


# 搜索图片
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        file = request.files['query_img']

        # Save query image
        img = Image.open(file.stream)  # PIL image
        # print(file.filename)
        uploaded_img_path = "static/uploaded/" + file.filename
        # print(uploaded_img_path)
        img.save(uploaded_img_path)

        # Run search
        dc = p_search(uploaded_img_path)
        # 得到查询结果
        answers = dc.get()[0]

        # 删除上一次上传的图片
        global last_upload_img
        print(last_upload_img)
        if last_upload_img is not None and len(last_upload_img) != 0:
            if os.path.exists(last_upload_img):
                os.remove(last_upload_img)
            else:
                print('删除上一次上传图片失败:', last_upload_img)

        last_upload_img = config.FILE_DIR + '/' + uploaded_img_path

        return render_template('index.html',
                               query_path=urllib.parse.quote(uploaded_img_path),
                               scores=answers)
    else:
        return render_template('index.html')


# Load image path
def load_image(folderPath):
    for filePath in glob(folderPath):
        if os.path.splitext(filePath)[1] in config.types:
            yield filePath


# Embedding pipeline
p_embed = (
    pipe.input('src')
    # 传入src，输出img_path
    .flat_map('src', 'img_path', load_image)
    # 传入img_path，输出img
    .map('img_path', 'img', image_decode_custom)
    # 传入img，输出vec
    .map('img', 'vec', ops.image_embedding.timm(model_name='resnet50'))
)

# Search pipeline
p_search_pre = (
    p_embed.map('vec', 'search_res', feature_search)
)
# 输出 search_res
p_search = p_search_pre.output('search_res')


if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)
