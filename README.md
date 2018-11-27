# Web Crawler using Scrapy
- Applied login simulation, random User Agent and random IP proxy to avoid anti-scraping blacklisted. I finally discarded IP proxy part because the websites I crawled on never blocked me...
- Implemented 2 spiders in this project, one for collecting tech articles information on jobbole.com, the other for collecting users' public profile on linkedin.com.
- Implemented 2 types of database storage here, one is MySQL and the other is Elasticsearch.
- Implemented a pipeline to parse the user profile from linkedin, generate the inverted index and completion suggester field, finally store into Elasticsearch.
- Choose LinkedinSpider + LinkedinPipeline + Elastisearch to generate database for a search engine "Lnkn", another project of mine. See: https://github.com/Nifoo/Lnkn
