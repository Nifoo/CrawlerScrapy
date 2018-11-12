# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class JobboleArticleItem(scrapy.Item):
    title = scrapy.Field()
    date = scrapy.Field()
    url = scrapy.Field()
    urlObjId = scrapy.Field()
    coverImgUrl = scrapy.Field()
    coverImgFilePath = scrapy.Field()
    thumbUp = scrapy.Field()
    favNum = scrapy.Field()
    commentNum = scrapy.Field()
    tags = scrapy.Field()
    content = scrapy.Field()

    @staticmethod
    def get_img_url(self):
        return 'coverImgUrl'

    @staticmethod
    def get_img_path():
        return 'coverImgFilePath'

    def get_insert_sql(self):
        insert_sql = '''            
                insert into article_jobbole(title, url, url_obj_id, cover_img_url, cover_img_file_path, thumb_up, 
                fav_num, comment_num, tags, content, create_date) 
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
        params = (self['title'], self['url'], self['urlObjId'], self['coverImgUrl'],
                  self['coverImgFilePath'], self['thumbUp'], self['favNum'], self['commentNum'],
                  self['tags'], self['content'], self['date'])
        return insert_sql, params


class ZhihuQaItem(scrapy.Item):
    topic = scrapy.Field()
    subtopic = scrapy.Field()
    question_id = scrapy.Field()
    question_title = scrapy.Field()
    question_content = scrapy.Field()
    answer_id = scrapy.Field()
    answer_content = scrapy.Field()
    answer_username = scrapy.Field()
    answer_url = scrapy.Field()
    thumb_up_num = scrapy.Field()
    helpful_num = scrapy.Field()
    comment_num = scrapy.Field()
    edit_date = scrapy.Field()
    create_date = scrapy.Field()
    update_date = scrapy.Field()


class LinkedinItem(scrapy.Item):
    id = scrapy.Field()
    parent_id = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()
    occupation = scrapy.Field()
    # location = scrapy.Field()
    photo_url = scrapy.Field()
    photo_path = scrapy.Field()

    # # List of Dict [{'companyName':, 'title':, 'startDate':, 'endDate':, }]
    # experience = scrapy.Field()
    #
    # # List of Dict [{'schoolName':, 'fieldOfStudy':, 'degreeName':, 'startDate':, 'endDate':}]
    # education = scrapy.Field()
    #
    # # List of links
    # similiar_lk = scrapy.Field()

    @staticmethod
    def get_img_url():
        return 'photo_url'

    @staticmethod
    def get_img_path():
        return 'photo_path'

    def get_insert_sql(self):
        insert_sql = '''insert ignore into lk_person(id, url, name, occupation, photo_url, photo_path) values (%s, %s, %s, %s, %s, %s)'''
        params = (self['id'], self['url'], self['name'], self['occupation'],
                  self['photo_url'], self['photo_path'])
        return insert_sql, params

    def get_insert_sql2(self):
        insert_sql = '''insert ignore into lk_relation(id_from, id_to) values(%s, %s)'''
        params = (self['parent_id'], self['id'])
        return insert_sql, params
