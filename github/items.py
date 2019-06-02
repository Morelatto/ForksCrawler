# -*- coding: utf-8 -*-
import re
import scrapy

from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join, Compose
from w3lib.html import strip_html5_whitespace


def parse_commit_text(t):
    return re.findall(r'(\d+) commits? ([a-n]+)', t)


class GitHubRepo(scrapy.Item):
    user = scrapy.Field()
    name = scrapy.Field()

    watchers = scrapy.Field()
    stars = scrapy.Field()
    forks = scrapy.Field()

    commits = scrapy.Field()
    branches = scrapy.Field()
    releases = scrapy.Field()
    contributors = scrapy.Field()
    license = scrapy.Field()

    branch = scrapy.Field()
    fork_commits = scrapy.Field()
    last_updated = scrapy.Field()


def parse_number(n):
    return int(n.replace(',', ''))


class GitHubRepoLoader(ItemLoader):
    default_item_class = GitHubRepo
    default_input_processor = MapCompose(strip_html5_whitespace)
    default_output_processor = Compose(TakeFirst())

    watchers_out = Compose(TakeFirst(), parse_number)
    stars_out = Compose(TakeFirst(), parse_number)
    forks_out = Compose(TakeFirst(), parse_number)
    contributors_out = Compose(TakeFirst(), parse_number)

    fork_commits_in = MapCompose(strip_html5_whitespace)
    fork_commits_out = Compose(Join(), parse_commit_text)
