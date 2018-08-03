# Author: Yan Zhang
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from wiki_scraper.spiders.wiki_philosophy import WikiPhilosophySpider


# Crawl wiki for multiple times, the csv result file will be created/updated.
process = CrawlerProcess(get_project_settings())
process.crawl(WikiPhilosophySpider)
process.start()