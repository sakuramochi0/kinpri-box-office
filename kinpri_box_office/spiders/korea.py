# -*- coding: utf-8 -*-
import re
from dateutil.parser import parse

import scrapy


class KoreaSpider(scrapy.Spider):
    name = "korea"
    allowed_domains = ["namu.wiki"]
    start_urls = ['https://namu.wiki/w/KING%20OF%20PRISM%20PRIDE%20the%20HERO']

    def parse(self, response):
        for table in response.css('.wiki-table'):
            # find box office table
            if '누적 관객수'in table.css('tr').extract_first():
                for i, row in enumerate(table.css('tr')):
                    # skip headers
                    if i < 3:
                        continue
                    col_num = len(row.css('td ::text').extract())
                    # first date of each week
                    if col_num == 9:
                        date = row.css('td:nth-child(2) ::text').extract_first()
                        sell = row.css('td:nth-child(3) ::text').extract_first()
                        box_office = row.css('td:nth-child(6) ::text').extract_first()
                    # other dates
                    elif col_num == 4:
                        date = row.css('td:nth-child(1) ::text').extract_first()
                        sell = row.css('td:nth-child(2) ::text').extract_first()
                        box_office = row.css('td:nth-child(4) ::text').extract_first()
                    # skip the date without data
                    if '-' in sell:
                        continue
                    date = parse(re.search(r'\d{4}-\d{2}-\d{2}', date).group(0))
                    sell = int(re.search(r'[\d,]+', sell).group(0).replace(',', ''))
                    box_office = int(re.search(r'[\d,]+', box_office).group(0).replace(',', ''))
                    yield dict(
                        _id=date,
                        sell=sell,
                        box_office=box_office
                    )
