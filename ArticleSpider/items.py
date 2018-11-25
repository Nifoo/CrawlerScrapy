# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

from ArticleSpider.models.es_types import LkPersonType

from elasticsearch_dsl.connections import connections

es = connections.create_connection(hosts=["localhost"])


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
    location = scrapy.Field()
    photo_url = scrapy.Field()
    photo_path = scrapy.Field()
    summary = scrapy.Field()
    company_exp = scrapy.Field()
    company_jobexp = scrapy.Field()
    school_exp = scrapy.Field()

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

    def save_to_es(self):
        lk_person = LkPersonType()
        lk_person.name = self['name']
        lk_person.occupation = self['occupation']
        lk_person.location = self['location']
        lk_person.url = self['url']
        lk_person.photo_url = self['photo_url']
        lk_person.photo_path = self['photo_path']

        lk_person.summary = self['summary']
        lk_person.company_exp = self['company_exp']
        lk_person.company_jobexp = self['company_jobexp']
        lk_person.school_exp = self['school_exp']

        lk_person.beauty_score = 0
        lk_person.gender = ''

        lk_person.suggest = gen_suggests(LkPersonType.Index.name,
                                         ((lk_person.occupation, 40), (lk_person.location, 4),
                                          (lk_person.summary, 10), (lk_person.company_exp, 5),
                                          (lk_person.company_jobexp, 5), (lk_person.school_exp, 2),
                                          (lk_person.name, 2)))

        lk_person.save(using=None, index=None, id=self['id'], validate=True, skip_empty=True)
        return


# generate suggested word[] with scores, according to record
def gen_suggests(index, param):
    used_words = set()
    suggests = []
    for text, weight in param:
        if text:
            # es. analyze
            words = es.indices.analyze(index=index, body=text, params={'analyzer': "ik_max_word"})
            # analyzed_words = set(r["token"] for r in words["tokens"] if len(r["token"]) > 1)
            analyzed_words = set(r["token"] for r in words["tokens"])
            new_words = analyzed_words - used_words
        else:
            new_words = set()
        if new_words:
            suggests.append({"input": list(new_words), "weight": weight})
    return suggests
