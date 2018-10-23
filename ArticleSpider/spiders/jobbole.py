# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse

from ArticleSpider.items import JobboleArticleItem


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    # Scrapy will make request to start_urls with parse() as call back.

    # extract detailed page urls from the overview page, yield a RequestForUrl + parse_detail for each page;
    # after visit the urls in current overview page, yield a RequestForNextPage + parse;
    def parse(self, response):
        # Use CSS selector instead of Xpath selector (they have the same effect) to select detailed urls list
        # select all nodes: id=archive / class=post && floated-thumb / class=post-thumb / tag=a
        detailNodes = response.css("#archive .post.floated-thumb .post-thumb a")
        for detailNode in detailNodes:
            # print(detailedUrl)
            # Asynchronous request (Scrapy help to handle) for detailed page, and then call "parse_detail"
            # "Request" is in scrapy.http; "parse.urljoin" is in urllib, to generate a complete url (sometimes detailed url is a relative url).
            # (Assume the coverPicture for each article can only be seen on the overview page (not the detailed page), then we need get the picture and pass into parse_detail, using "meta")
            imgSrc = detailNode.css("img::attr(src)").extract_first()
            detailUrl = detailNode.css("::attr(href)").extract_first()
            yield Request(parse.urljoin(response.url, detailUrl), meta={"coverImg": imgSrc}, callback=self.parse_detail)

        # Find next overview page, make request and call self (parse()) again.
        # .extract_first(defaultValue) return defaultValue if no ele in extracted list; or return the first ele in list
        nextUrl = response.css(".navigation .next.page-numbers::attr(href)").extract_first("")
        if nextUrl:
            yield Request(nextUrl, callback=self.parse)
        pass

    # parse information for a detailed page
    def parse_detail(self, response):
        # DOM元素id是全局唯一的；
        # scrapy 获取的源码是未执行js动态生成时的html源码（相当于browser中查看源码）；
        # 而直接从browser通过开发者工具xpath Copy拿到的xpath是基于js执行动态生成后的html；
        # 因此通过从browser复制得到类似/div[1]/div[2]...这样的xpath有时是不靠谱的；
        # 而类似"*[@id="..."]"包含id 或者 "*[@class="header"]/..."包含实际内容class的 这样的比较靠谱
        # re_selector = response.xpath('//*[@id="post-114442"]/div[1]/h1')

        # response.xpath(...) 返回的是SelectorList;
        # 此处Selector元素[0]：<Selector xpath='//*[@class="entry-meta"]/p[1]/text()' data='\r\n\r\n            2018/10/15 ·  '>
        # (Selector or SelectorList) .extract() 返回( data or dataList)

        coverImg = response.meta.get("coverImg", "")
        title = response.css(".entry-header h1::text").extract_first()
        date = response.xpath('//*[@class="entry-meta"]/p[1]/text()')[0].extract().replace('·', '').strip()

        # < span data - post - id = "114442"class =" btn-bluet-bigger href-style vote-post-up   register-user-only " > < i class ="fa  fa-thumbs-o-up" > < / i > < h10 id="114442votetotal" > 1 < / h10 > 赞 < / span >
        thumbUp = int(response.xpath("//span[contains(@class, 'vote-post-up')]/h10/text()").extract()[0])

        favSpan = response.xpath("//span[contains(@class, 'bookmark-btn')]/text()").extract()[0];
        favMatch = re.match(".*?(\d+).*", favSpan)
        if favMatch:
            favNum = int(favMatch.group(1))
        else:
            favNum = 0

        comment = response.xpath("//a[@href='#article-comment']/span/text()").extract()[0]
        commentMatch = re.match('.*?(\d+).*', comment)
        if commentMatch:
            commentNum = int(commentMatch.group(1))
        else:
            commentNum = 0

        tagList = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a/text()").extract()
        # Delete "k 评论" tag
        tagList = [element for element in tagList if not (element.strip().endswith("评论"))]
        tags = ",".join(tagList)

        contentList = response.css("div.entry *::text").extract()
        content = " ".join(contentList)
        content = content.replace("\t", " ").replace("\n", " ").replace("\r", " ")
        content = " ".join(content.split())

        item = JobboleArticleItem()
        item["title"] = title
        item["date"] = date
        item["url"] = response.url
        # item["urlObjId"]
        item["coverImgUrl"] = coverImg
        item["thumbUp"] = thumbUp
        item["favNum"] = favNum
        item["commentNum"] = commentNum
        item["tags"] = tags
        item["content"] = content

        #yield send item to pipeline if "settings" enable pipleline
        yield item

        # title = scrapy.Field()
        # date = scrapy.Field()
        # url = scrapy.Field()
        # urlObjId = scrapy.Field()
        # coverImgUrl = scrapy.Field()
        # thumbUp = scrapy.Field()
        # favNum = scrapy.Field()
        # commentNum = scrapy.Field()
        # tags = scrapy.Field()
        # content = scrapy.Field()
        pass
