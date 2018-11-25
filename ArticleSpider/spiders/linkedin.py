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
    seed_url = 'https://www.linkedin.com/in/jiaxi-wang-2b9817124/'
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

        html_parser = HTMLParser.HTMLParser()

        itemA = response.meta.get('item', '')
        item = LinkedinItem(itemA)
        if item:
            data_strs = response.css('code[style="display: none"]::text').extract()
            tar_str = ''
            tar_len = 0
            company_exp = []
            school_exp = []
            company_jobexp = []
            for data_str in data_strs:
                if len(data_str) > tar_len:
                    tar_str = data_str
                    tar_len = len(tar_str)
            if tar_str:
                obj_jsn = json.loads(tar_str)
                tar_jsn = obj_jsn['included']
                for mp in tar_jsn:
                    if "headline" in mp:
                        item['location'] = mp.get('locationName', '')
                    if "companyName" in mp:
                        start_time = 'NA'
                        end_time = 'NA'
                        if 'timePeriod' in mp:
                            if 'startDate' in mp['timePeriod']:
                                start_time = str(mp['timePeriod']['startDate'].get('year', 'NA'))
                            if 'endDate' in mp['timePeriod']:
                                end_time = str(mp['timePeriod']['endDate'].get('year', 'NA'))
                        company_exp.append(
                            mp['companyName'] + ', ' + mp.get('title', '') + ', ' + start_time + '-' + end_time)
                        company_jobexp.append(mp['companyName'] + ', ' + mp.get('description', ''))
                    if "schoolName" in mp:
                        start_time = 'NA'
                        end_time = 'NA'
                        if 'startDate' in mp['schoolName']:
                            start_time = str(mp['startDate'].get('year', 'NA'))
                        if 'endDate' in mp['schoolName']:
                            end_time = str(mp['endDate', ''].get('year', 'NA'))
                        school_exp.append(
                            mp['schoolName'] + ', ' + mp.get('fieldOfStudy', '') + ', ' + mp.get('degreeName',
                                                                                                 '') + ', ' + start_time + '-' + end_time)
                    if 'summary' in mp:
                        item['summary'] = mp['summary']
                item['company_exp'] = ". ".join(company_exp)
                item['company_jobexp'] = ". ".join(company_jobexp)
                item['school_exp'] = ". ".join(school_exp)

            yield item
        url = response._url
        lk_id = url[len("https://www.linkedin.com/in/"):-1]

        cookie = response.request.headers.getlist('Cookie')
        cookie_str = re.match('.*JSESSIONID="(.*?)";.*', cookie[0]).group(1)
        self.headers.update({'csrf-token': cookie_str})
        recmd_url = self.recmd_url_prefix + str(lk_id) + self.recmd_url_postfix
        yield Request(url=recmd_url, method='GET', headers=self.headers, dont_filter=True,
                      callback=self.parse_recmd_lst, meta={'parent_id': lk_id})
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
            item = {}
            item['id'] = prof['publicIdentifier']
            item['parent_id'] = parent_id
            ele_url = 'https://www.linkedin.com/in/' + prof['publicIdentifier'] + '/'
            item['url'] = ele_url
            item['name'] = prof['firstName'] + prof['lastName']
            item['occupation'] = prof['occupation']
            if 'picture' in prof:
                photo_obj = prof['picture']["com.linkedin.common.VectorImage"]
                item['photo_url'] = [photo_obj["rootUrl"] + photo_obj["artifacts"][3]["fileIdentifyingUrlPathSegment"]]
            yield Request(url=ele_url, method='GET', headers=self.headers, dont_filter=True,
                          callback=self.parse_profile, meta={'item': item})
        pass
