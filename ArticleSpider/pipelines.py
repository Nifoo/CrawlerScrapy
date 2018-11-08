# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
from scrapy.pipelines.images import ImagesPipeline


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class ArticleImagePipeline(ImagesPipeline):
    # many functions can be overriden, see ImagesPipeline
    def item_completed(self, results, item, info):
        for succ, value in results:
            image_file_path = value["path"]
        item["coverImgFilePath"] = image_file_path
        return item


class MySqlPipeline(object):

    # DB related operation: conn = MySQLdb.connect(...), cursor = conn.cursor()
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1', 'root', '19920105hp', 'crawler', charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()
        self.conn.autocommit(on=True)

    def process_item(self, item, spider):
        insert_sql = '''            
            insert into article_jobbole(title, url, url_obj_id, cover_img_url, cover_img_file_path, thumb_up, 
            fav_num, comment_num, tags, content, create_date) 
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        self.cursor.execute(insert_sql, (item['title'], item['url'], item['urlObjId'], item['coverImgUrl'],
                                         item['coverImgFilePath'], item['thumbUp'], item['favNum'], item['commentNum'],
                                         item['tags'], item['content'], item['date']))
        return item
