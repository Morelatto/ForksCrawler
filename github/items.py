# -*- coding: utf-8 -*-
import re
import scrapy

from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join, Compose
from w3lib.html import strip_html5_whitespace


def parse_commit_text(t):
    return re.findall(r'(\d+) commits? ([a-n]+)', t)


class GitHubItem(scrapy.Item):
    user = scrapy.Field()
    repo = scrapy.Field()
    branch = scrapy.Field()
    commits = scrapy.Field()
    update_date = scrapy.Field()

    def __repr__(self):
        return str(dict(self))


class GitHubItemLoader(ItemLoader):
    default_item_class = GitHubItem
    default_output_processor = TakeFirst()

    commits_in = MapCompose(strip_html5_whitespace)
    commits_out = Compose(Join(), parse_commit_text)
