import scrapy

from github.items import GitHubItemLoader

GITHUB = 'github.com'
FORKS = '/network/members'

TEXT_SEL = '::text'
ATTR_SEL = '::attr(%s)'


class GitHubForksSpider(scrapy.Spider):
    name = 'forks'
    allowed_domains = [GITHUB]

    def __init__(self, addr, *args, **kwargs):
        super(GitHubForksSpider, self).__init__(*args, **kwargs)
        self.user, self.repo = addr.split('/')

    def start_requests(self):
        yield scrapy.Request(url='https://%s/%s/%s/%s' % (GITHUB, self.user, self.repo, FORKS))

    def parse(self, response):
        for fork in response.css('.repo'):
            links = fork.css('a::attr(href)').getall()
            yield scrapy.Request(url=response.urljoin(links[-1]), callback=self.parse_fork)

    def parse_fork(self, response):
        loader = GitHubItemLoader(response=response)
        urls = response.url.split('/')
        loader.add_value('user', urls[3])
        loader.add_value('repo', urls[4])
        loader.add_css('branch', '#branch-select-menu .btn .css-truncate-target' + TEXT_SEL)
        loader.add_css('commits', '.branch-infobar' + TEXT_SEL)
        loader.add_css('update_date', '.commit-tease .no-wrap span *' + TEXT_SEL)

        item = loader.load_item()
        self.logger.info(item)
        return item
