# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request

from ArticleSpider.items import ZhihuQaItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"
    header = {"User-Agent": agent}

    def start_requests(self):
        # Here use async IO offered by Scrapy. (Or use traditional sync method like Requests.get(...), re.match()...)
        # If not assign "callback func", scrapy would call "parse" by default.

        # Scrapy/crawler.py expects the return value of start_requests() is iterable so use [...], see:
        # Ln81: start_requests = iter(self.spider.start_requests())

        return [
            Request("https://www.zhihu.com/topics", method="GET", headers=self.header, callback=self.parse_topics_page)]

    def parse_topics_page(self, response):
        topics = response.css(".zm-topic-cat-item")
        topic_ids = topics.css("::attr(data-id)").extract()
        topic_names = topics.css("::text").extract()
        # for (topic_id, topic_name) in zip(topic_ids, topic_names):
        for topic_name in topic_names:
            url = "https://www.zhihu.com/topics#" + topic_name
            yield Request(url, headers=self.header, callback=self.parse_subtopics_page, dont_filter=True,
                          meta={"topic": topic_name})

    # 不同topic对应的html实际是一样的（都是第一个topic的样子），其他topic都是动态刷新的，因此目前该写法有问题
    def parse_subtopics_page(self, response):
        base_meta = response.meta
        subtopics = response.css(".item")
        subtopic_links = subtopics.css('.blk a[target="_blank"]::attr(href)').extract()
        subtopic_names = subtopics.css('.blk a[target="_blank"] strong::text').extract()
        for (subtopic_link, subtopic_name) in zip(subtopic_links, subtopic_names):
            base_meta.update({"subtopic": subtopic_name})
            yield Request("https://www.zhihu.com" + subtopic_link + "/top-answers/", headers=self.header,
                          callback=self.parse_subtopic_hot_answers_page, dont_filter=True,
                          meta=base_meta)
        pass

    def parse_subtopic_hot_answers_page(self, response):
        # hot_answers from default static response page only contains 5 answers.
        # Actually others would be loaded by AJAX and JS when mouse wheels down.
        # to-do: use Selenium and PhantomJS to load these dynamic content into Scrapy
        base_meta = response.meta  # topic, subtopic
        hot_answers = response.css(".List-item.TopicFeedItem")
        hot_answers_item = hot_answers.css(".ContentItem.AnswerItem")
        hot_answers_links = hot_answers_item.css(
            '.ContentItem-title a[data-za-detail-view-element_name="Title"]::attr(href)').extract()
        for hot_answers_link in hot_answers_links:
            yield Request("https://www.zhihu.com" + hot_answers_link, headers=self.header,
                          callback=self.parse_hot_answer_page, dont_filter=True, meta=base_meta)

        pass

    def parse_hot_answer_page(self, response):

        pass
