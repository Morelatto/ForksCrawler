import scrapy

from github.items import GitHubRepoLoader

GITHUB = 'github.com'

TEXT_SEL = '::text'
ATTR_SEL = '::attr(%s)'

PAGE_HEAD_ACTIONS = '.pagehead-actions li:nth-child(%d) .social-count' + TEXT_SEL

STATS_BAR = '.numbers-summary li:nth-child(%d)'
NUM_TEXT = ' .num' + TEXT_SEL

BRANCH_NAME = '#branch-select-menu .btn span' + TEXT_SEL
FORK_COMMITS_AHEAD_BEHIND = '.branch-infobar' + TEXT_SEL
LAST_COMMIT = 'span[itemprop=dateModified] relative-time::attr(datetime)'


class GitHubRepoSpider(scrapy.Spider):
    name = 'repo'
    allowed_domains = [GITHUB]

    def __init__(self, user_repos, *args, **kwargs):
        super(GitHubRepoSpider, self).__init__(*args, **kwargs)
        self.start_urls = ['https://' + GITHUB + user_repo for user_repo in user_repos.split(';')]

    def parse(self, response):
        loader = GitHubRepoLoader(response=response)
        url = response.url.split('/')
        loader.add_value('user', url[3])
        loader.add_value('name', url[4])

        loader.add_css('watchers', PAGE_HEAD_ACTIONS % 1)
        loader.add_css('stars', PAGE_HEAD_ACTIONS % 2)
        loader.add_css('forks', PAGE_HEAD_ACTIONS % 3)

        loader.add_css('commits', STATS_BAR % 1 + NUM_TEXT)
        loader.add_css('branches', STATS_BAR % 2 + NUM_TEXT)
        loader.add_css('releases', STATS_BAR % 3 + NUM_TEXT)
        loader.add_css('contributors', STATS_BAR % 4 + NUM_TEXT)
        loader.add_css('license', STATS_BAR % 5 + ' a' + TEXT_SEL)

        loader.add_css('branch', BRANCH_NAME)
        loader.add_css('fork_commits', FORK_COMMITS_AHEAD_BEHIND)
        loader.add_css('last_updated', LAST_COMMIT)

        item = loader.load_item()
        self.logger.info(item)
        return item
