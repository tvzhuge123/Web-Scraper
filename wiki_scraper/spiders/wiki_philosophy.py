# Author: Yan Zhang
import scrapy, re, csv, os
from wiki_scraper.items import WikiScraperItem


class WikiPhilosophySpider(scrapy.Spider):
    name = 'wiki_philosophy'
    allowed_domains = ['en.wikipedia.org']
    start_urls = ['https://en.wikipedia.org/wiki/Special:Random']

    max_page = 500  # max number of wiki page needed
    page_count = 0  # total number of wiki page finished
    total_request = 0 # total http requests made

    goal = 'Philosophy'  # destination page
    threshold = 1000  # max http requests allowed for a single process
    status_code = {1: 'In progress', 0: 'Philosophy found!', -1: 'Exceeded max request limit.', -2: 'Infinite loop.', -3: 'Dead end.'}
    file_path = 'history_data.csv'  # path of history data
    history_result = {}  # key: wiki page heading, value: length of path to Philosophy.

    def parse(self, response):
        link = ''
        heading = response.xpath('//h1[@id="firstHeading"]/text()').extract_first()
        # In some wiki pages, heading is italic.
        if heading is None:
            heading = response.xpath('//h1[@id="firstHeading"]/i/text()').extract_first()

        # For the initial visit, define initial length to be 1, create a list that contains headings of visited pages.
        if 'item' not in response.meta:
            item = WikiScraperItem()
            item['depth'] = 1
            item['status'] = 1
            item['visited_list'] = [heading]
            # Read history data from local drive.
            if os.path.isfile(WikiPhilosophySpider.file_path):
                with open(WikiPhilosophySpider.file_path, mode='r') as infile:
                    reader = csv.reader(infile)
                    WikiPhilosophySpider.history_result = {rows[0]: rows[1] for rows in reader}
        # If not the initial visit, increase current length by 1, append current heading to the list.
        else:
            item = response.meta['item']
            item['depth'] += 1
            item['visited_list'].append(heading)

        # Print current page heading.
        # print(str(item['depth']) + '. ' + heading)

        # Check history data, if current page has already been scraped, no need to continue scraping.
        if heading in WikiPhilosophySpider.history_result.keys():
            item['status'] = 0
        # If Philosophy has been found, exit. If not, search the next page.
        elif heading == WikiPhilosophySpider.goal:
            pass
        # Check if we have reached max http requests.
        elif item['depth'] >= WikiPhilosophySpider.threshold:
            item['status'] = -1
        # Check if it is looping back to a visited page.
        elif heading in item['visited_list'][:-1]:
            item['status'] = -2
            item['visited_list'].pop(-1)
        else:
            # Find the next wiki page link.
            link = self.next_link(response)
            if not link:
                item['status'] = -3

        # Current process finished, reset variables to start new.
        if not link:
            self.update_history(item, heading)
            print(WikiPhilosophySpider.page_count, "pages crawled.")
            WikiPhilosophySpider.total_request += item['depth']
            if WikiPhilosophySpider.page_count < WikiPhilosophySpider.max_page:
                yield scrapy.Request(WikiPhilosophySpider.start_urls[0], callback=self.parse, dont_filter=True)
            else:
                print("In total,", WikiPhilosophySpider.page_count, "pages finished with", WikiPhilosophySpider.total_request, "http requests")
        # Go to next page.
        else:
            yield scrapy.Request('http://en.wikipedia.org' + link, callback=self.parse, meta={'item': item}, dont_filter=True)


    def next_link(self, response):
        pars = []
        if len(response.xpath('//div[@id="mw-content-text"]//p//@href').extract()) != 0 :
            pars = response.xpath('//div[@id="mw-content-text"]//p').extract()
            # Skip link in the tale on the right side and link for coordinates.
            tmp = response.xpath('//div[@id="mw-content-text"]//table//p').extract()
            if (len(tmp) > 0 and pars[0] == tmp[0]) or '<span id="coordinates">' in pars[0]:
                pars = pars[1:]
        # Pages with only lists in the main text.
        pars = pars + response.xpath('//div[@id="mw-content-text"]//ul[not(ancestor::table)]/li').extract()

        for par in pars:
            # Skip link in italic.
            par = par.replace('<i>', '(')
            par = par.replace('</i>', ')')
            # Skip link inside parenthesis.
            par = self.parse_pattern(par, '(', ')')
            pattern = r'(?<=<a href=")/wiki/[0-9a-zA-Z\(\)\-\.,_%#]*?(?=")'
            link = re.search(pattern, par)
            if link:
                return link.group(0)


    def parse_pattern(self, string, pattern_left, pattern_right):
        # Following code only works for regular cases.
        # It's not applicable for irregular cases like ")" apperears before "(", or one of "(" is not paired with ")".
        # The irregular cases and syntax error will most likely not in the text or paragraph in wiki pages.
        if pattern_left in string and pattern_right in string:
            result = ''
            tmp_pattern = 0
            tmp_tag = 0
            for s in string:
                if s == '<':
                    tmp_tag += 1
                elif s == '>':
                    tmp_tag -= 1
                elif s == pattern_left and tmp_tag == 0:
                    tmp_pattern += 1
                    continue
                elif s == pattern_right and tmp_tag == 0:
                    tmp_pattern -= 1
                    continue
                if tmp_pattern <= 0:
                    result += s
        else:
            result = string
        return result


    def update_history(self, item, heading):
        new_result = {}
        if item['status'] == 0:
            if int(WikiPhilosophySpider.history_result[heading]) > 0:
                for i, page in enumerate(item['visited_list'][:-1], 1):
                    new_result[page] = int(WikiPhilosophySpider.history_result[heading]) + len(item['visited_list']) - i
            else:
                for page in item['visited_list'][:-1]:
                    new_result[page] = WikiPhilosophySpider.history_result[heading]
            WikiPhilosophySpider.page_count += len(new_result)
        elif item['status'] == 1:
            for i, page in enumerate(item['visited_list']):
                new_result[page] = len(item['visited_list']) - i
            WikiPhilosophySpider.page_count += len(new_result)
        elif item['status'] == -1:
            new_result[heading] = item['status']
        else:
            for page in item['visited_list']:
                new_result[page] = item['status']

        # Update/Create history data file.
        if os.path.isfile(WikiPhilosophySpider.file_path):
            mode = 'a'
        else:
            mode = 'w'
        with open(WikiPhilosophySpider.file_path, mode) as outfile:
            writer = csv.writer(outfile)
            for key, value in new_result.items():
                writer.writerow([key, value])
