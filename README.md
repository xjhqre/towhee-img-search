# towhee-img-search
towhee+elasticsearch实现本地以图搜图

elasticsearch版本为 7.4.2

elasticsearch安装方法参考我的这篇文章：[全文检索-ElasticSearch](https://blog.csdn.net/xjhqre/article/details/124553312)



## 使用方法

一、使用 OSS 存储图片，将图片库上传到 OSS。

二、创建 elasticsearch 索引。

```json
# 创建索引结构
PUT imgsearch
{
  "mappings": {
    "properties": {
      "feature": {
        "type": "dense_vector",
        "dims": 1024
      },
      "url": {
        "type": "keyword"
      },
      "name": {
        "type": "keyword"
      }
    }
  }
}
```

三、修改 config.py 中的配置。

四、运行 extractFeatures.py，提取图片特征向量并存储到elasticsearch。

五、运行 searchServer.py，启动 web 服务。



## 演示

![image-20230408195553888](https://typora-xjhqre.oss-cn-hangzhou.aliyuncs.com/img/202304081956985.png)
