# -*- coding: utf-8 -*-
import re
import scrapy
import zenhan
from dateutil.parser import parse


def normalize(text):
    return zenhan.z2h(text, mode=zenhan.DIGIT|zenhan.ASCII)


def is_kinpri(text):
    return re.search(r'king of prism', text, flags=re.I) \
        and not re.search(r'pride', text, flags=re.I)


class MimorinDailySpider(scrapy.Spider):
    name = 'mimorin_daily_kinpri1'
    allowed_domains = ['mimorin2014.blog.fc2.com']
    start_urls = ['http://mimorin2014.blog.fc2.com/blog-category-6.html/']

    def parse(self, response):
        for entry in response.css('.entry[id]'):
            title = entry.css('.entry_header a::text').extract_first()

            # stop before kinpri2 is published
            if '20160108' in title:
                return
            
            if 'デイリー合算ランキング' in title and '中間' not in title:
                yield scrapy.Request(
                    url=entry.css('a::attr(href)').extract_first(),
                    callback=self.parse_entry,
                )

        next_url = response.css('link[rel="next"]::attr(href)').extract_first()
        yield response.request.replace(url=next_url)

    def parse_entry(self, response):
        date = parse(response.css('.entry_header::text').re(r'\d+')[0])
        lines = response.css('.entry_body::text').extract()
        # filter empty lines
        lines = list(i for i in filter(lambda x: x.strip(), lines))
        # remove headers
        lines = lines[2:]
        # split columns
        lines = list(map(lambda x: x.split(), lines))
        # convert string to int
        new_lines = []
        for line in lines:
            title = normalize(' '.join(line[6:]))
            if not is_kinpri(title):
                continue
            int_list = map(int, map(lambda x: x.replace('*', ''), line[:5]))
            rank, sell, total_seat, show_num, theater_num = map(int, int_list)
            item = dict(
                rank=rank,
                sell=sell,
                total_seat=total_seat,
                show_num=show_num,
                theater_num=theater_num,
            )
            ratio_string = line[5].replace('*', '').replace('%', '')
            if ratio_string:
                item['ratio_last_week'] = float(ratio_string) / 100
            item['title'] = title
            item['_id'] = date
            yield item
