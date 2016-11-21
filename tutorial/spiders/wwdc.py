import csv
import scrapy
from scrapy import signals
from scrapy import Request
from scrapy.conf import settings
from tutorial.items import TutorialItem
from scrapy.xlib.pydispatch import dispatcher


class WwdcSpider(scrapy.Spider):
    name = "applewwdc"
    allowed_domains = ["apple.com"]
    sessions = {"sessions": []}

    def start_requests(self):
        years = [2012, 2013, 2014, 2015, 2016]
        for year in years:
            url = "https://developer.apple.com/videos/wwdc" + str(year)
            yield self.make_requests_from_url(url)

    def parse(self, response):
        sessions = response.xpath("//ul[@class='collection-items']/li[@class='collection-item ']")
        if sessions:
            for session in sessions:
                link = session.xpath("./section/section/section/a/@href").extract()
                title = session.xpath("./section/section/section//a/h5/text()").extract()
                print title[0], link[0]
                yyyy = response.url.split('/')[-1][-4:]
                meta = {"title": title[0], "year": yyyy}
                yield Request("https://developer.apple.com"+link[0], callback=self.parse_detail, meta={"meta": meta})

    def parse_detail(self, response):
        meta = response.meta["meta"]
        print response.url
        session_id = response.url.split('/')[-1]
        title = meta["title"]
        yyyy = meta["year"]
        sessionNumber = response.url.split('/')[-2]
        videos = ""
        docs = ""
        resource_links = response.xpath("//li[@data-supplement-id='resources']/ul[@class='links small']/li")
        for resource_link in resource_links:
            find_class = resource_link.xpath("./@class").extract()
            if find_class:
                if find_class[0] == 'video':
                    videos = resource_link.xpath("./ul/li/a/@href").extract()
                elif find_class[0] == 'document':
                    docs = resource_link.xpath("./a/@href").extract()[0]

        item = {}
        item["title"] = title
        item["year"] = int(yyyy)
        item["sessionNumber"] = int(sessionNumber)
        item["hdVideo"] = videos[0]
        item["sdVideo"] = videos[1]
        item["presentationSlides"] = docs
        self.sessions["sessions"].append(item)
        return self.sessions
