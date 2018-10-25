# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.images import ImagesPipeline

class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item

class ArticleImagePipeline(ImagesPipeline):
    # many functions can be overriden, see ImagesPipeline
    def item_completed(self, results, item, info):
        for succ, value in results:
            image_file_path = value["path"]
        item["coverImagFilePath"] = image_file_path
        return item