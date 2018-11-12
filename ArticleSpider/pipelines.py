# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
import MySQLdb.cursors
from scrapy.pipelines.images import ImagesPipeline
from twisted.enterprise import adbapi


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class ArticleImagePipeline(ImagesPipeline):
    # many functions can be overriden, see ImagesPipeline
    def item_completed(self, results, item, info):
        for succ, value in results:
            image_file_path = value["path"]

        # for jobbole
        # item["coverImgFilePath"] = image_file_path

        item[item.get_img_path()] = image_file_path
        return item


class MySqlPipeline(object):

    # DB related operation: conn = MySQLdb.connect(...), cursor = conn.cursor()
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1', 'root', '19920105hp', 'crawler', charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()
        self.conn.autocommit(on=True)

    # def process_item(self, item, spider):
    #     insert_sql = '''
    #         insert into article_jobbole(title, url, url_obj_id, cover_img_url, cover_img_file_path, thumb_up,
    #         fav_num, comment_num, tags, content, create_date)
    #         values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    #     '''
    #     self.cursor.execute(insert_sql, (item['title'], item['url'], item['urlObjId'], item['coverImgUrl'],
    #                                      item['coverImgFilePath'], item['thumbUp'], item['favNum'], item['commentNum'],
    #                                      item['tags'], item['content'], item['date']))
    #     return item


# Async DB operation based on async container (from twisted.enterprise import adbapi)
class MySqlTwistedPipeline(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool

    # @classmethod class initialization
    # @classmethod def from_settings(cls, settings){...}: would be called by spider at first,
    # import configurations from settings
    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        # **dbparams, see: https://blog.csdn.net/lbxoqy/article/details/70040420
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparams)
        return cls(dbpool)

    def process_item(self, item, spider):
        # MySQL insertion in Async operation with DB connection pool using twisted
        query = self.dbpool.runInteraction(self.do_insert, item)
        # handle with async insertion error
        query.addErrback(self.handle_error)

    def handle_error(self, failure):
        print(failure)

    def do_insert(self, cursor, item):
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)
        insert_sql2, params2 = item.get_insert_sql2()
        cursor.execute(insert_sql2, params2)
