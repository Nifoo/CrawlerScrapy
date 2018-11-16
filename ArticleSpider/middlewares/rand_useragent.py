from fake_useragent import UserAgent

from ArticleSpider.tools.rand_proxy import RandProxy


class RandUserAgentMiddleware(object):
    def __init__(self, crawler):
        super(RandUserAgentMiddleware, self).__init__()
        self.ua = UserAgent()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        request.headers.setdefault('User-Agent', self.ua.random)

        # request.meta["proxy"] = RandProxy.get_proxy()
