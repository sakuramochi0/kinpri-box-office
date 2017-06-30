# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from get_mongo_client import get_mongo_client


class KinpriBoxOfficePipeline(object):
    cli = get_mongo_client()
    db = cli.kinpri_box_office

    def process_item(self, item, spider):
        if self.db[spider.name].find_one({
                '_id': item['_id'],
                'final_result': False
        }):
            self.db[spider.name].update_one(
                {'_id': item['_id']},
                {'$set': item},
                upsert=True,
            )
        return item
