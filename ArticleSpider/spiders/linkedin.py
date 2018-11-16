# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import re
import json
import HTMLParser
import ConfigParser

from ArticleSpider.items import LinkedinItem, LinkedinItem


class LinkedinSpider(scrapy.Spider):

    name = 'linkedin'
    allowed_domains = ['www.linkedin.com']
    start_urls = ['http://www.linkedin.com/']
    agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"
    headers = {"User-Agent": agent}

    cf = ConfigParser.ConfigParser()
    cf.read('ArticleSpider/spiders/secret.conf')
    email = cf.get('lk', 'email')
    passwd = cf.get('lk', 'passwd')

    login_url = 'https://www.linkedin.com/uas/login-submit?loginSubmitSource=GUEST_HOME'
    seed_url = 'https://www.linkedin.com/in/rachel-tao-9a034597/'
    offset = 17

    recmd_url_prefix = 'https://www.linkedin.com/voyager/api/identity/profiles/'
    recmd_url_postfix = '/browsemapWithDistance'

    def start_requests(self):
        return [Request(url='https://www.linkedin.com/', method="GET", headers=self.headers, callback=self.login,
                        )]

    def login(self, response):
        csrf = response.css("#loginCsrfParam-login::attr(value)").extract_first()
        post_data = {
            'session_key': self.email,
            'session_password': self.passwd,
            'isJsEnabled': 'false',
            'loginCsrfParam': csrf,
        }
        return scrapy.FormRequest(url=self.login_url, formdata=post_data, headers=self.headers,
                                  callback=self.check_login)

    def check_login(self, response):
        if response.status == 200:
            yield Request(url=self.seed_url, method="GET", headers=self.headers, callback=self.parse_profile)

    def parse_profile(self, response):
        ## Hard to parse_profile page... give up. Only use "recommend api" to get other similar viewed users with few info (only name, photo, occupation)
        # item = LinkedinItem()
        # item = {}
        # url = response._url
        # item['lk_url'] = url
        # lk_id = url[len("https://www.linkedin.com/in/"):-1]
        # item['lk_id'] = lk_id
        # start_id_str = response.css('code[style="display: none"]::attr(id)').extract_first()
        # start_id_num = int(start_id_str[len("bpr-guid-"):])
        # tar_id_num = start_id_num + self.offset
        # bulk_data_str = response.css('#bpr-guid-' + str(tar_id_num) + '::text').extract_first()
        # bulk_data_jsn = json.loads(bulk_data_str)
        # tar_data_jsn = bulk_data_jsn['included']
        # html_parser = HTMLParser.HTMLParser()
        #

        # for mp in tar_data_jsn:
        #     if "firstName" in mp:
        #         item["firstName"] = mp["firstName"]
        #         item["lastName"] = mp["lastName"]
        #     if "locationName" in mp:
        #         item["locationName"] = mp["locationName"]
        #     if "picture" in mp:
        #         item["photo_url"] = html_parser.unescape(
        #             mp["picture"]["rootUrl"] + mp["picture"]["artifacts"][3]["fileIdentifyingUrlPathSegment"])
        #     if "occupation" in mp:
        #         item['occupation'] = mp['occupation']
        # get other users similar (in distance):

        url = response._url
        lk_id = url[len("https://www.linkedin.com/in/"):-1]

        cookie = response.request.headers.getlist('Cookie')
        cookie_str = re.match('.*JSESSIONID="(.*?)";.*', cookie[0]).group(1)
        self.headers.update({'csrf-token': cookie_str})
        recmd_url = self.recmd_url_prefix + str(lk_id) + self.recmd_url_postfix
        yield Request(url=recmd_url, method='GET', headers=self.headers, callback=self.parse_recmd_lst, meta={'parent_id': lk_id})
        pass

    def parse_recmd_lst(self, response):
        eles = []
        try:
            eles = json.loads(response.text)['elements']
        except:
            pass
        parent_id = response.meta.get('parent_id')
        for ele in eles:
            prof = ele['miniProfile']
            item = LinkedinItem()
            item['id'] = prof['publicIdentifier']
            item['parent_id'] = parent_id
            ele_url = 'https://www.linkedin.com/in/' + prof['publicIdentifier'] + '/'
            item['url'] = ele_url
            item['name'] = prof['firstName'] + prof['lastName']
            item['occupation'] = prof['occupation']
            photo_obj = prof['picture']["com.linkedin.common.VectorImage"]
            item['photo_url'] = [photo_obj["rootUrl"] + photo_obj["artifacts"][3]["fileIdentifyingUrlPathSegment"]]
            yield item
            yield Request(url=ele_url, method='GET', headers=self.headers, callback=self.parse_profile)
        pass
