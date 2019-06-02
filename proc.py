# -*- coding: utf-8 -*-
"""
Usage:
    proc.py forks <user> <repo>
    proc.py parse_forks [--file=JSON_RESULTS]
    proc.py stars <user> <repo>
    proc.py parse_stars [--file=JSON_RESULTS]
    proc.py -h | --help | --version

Options:
    --file=JSON_RESULTS  JSON file with results from spider [default: results.json]
"""
import json
import re

import requests

from docopt import docopt
from parsel import Selector
from scrapy import cmdline
from tabulate import tabulate

GITHUB = 'github.com'
RAW_GITHUB = 'raw.githubusercontent.com'
FORKS_URL = 'network/members'
RESULTS_JSON = 'results.json'

cmd = ["scrapy", "crawl", "repo", "-a"]


def forks():
    execute(get_forks_repos(args['<user>'], args['<repo>']))
    print_fork_repos(parse_fork_repos())


# TODO
def stars():
    execute(get_readme_repos(args['<user>'], args['<repo>']))
    print_repos_stars(parse_repo_stars())


def execute(repos):
    cmd.append('repos=' + json.dumps(repos))
    try:
        cmdline.execute(cmd)
    except BaseException:
        pass


# Scrapy creates invalid json
def parse_scrapy_json(file_lines):
    for line in file_lines:
        yield json.loads(line)


def get_forks_repos(user, repo):
    r = requests.get('https://{}/{}/{}/{}'.format(GITHUB, user, repo, FORKS_URL))
    if r.status_code == 200:
        sel = Selector(text=r.text)
        return [(url.split('/')[1:]) for url in sel.css('.repo a:last-child::attr(href)').getall()]
    else:
        print('{}/{} not found'.format(user, repo))


def get_readme_repos(user, repo):
    r = requests.get('https://{}/{}/{}/master/README.md'.format(RAW_GITHUB, user, repo))
    if r.status_code == 200:
        url_re = re.compile(r"[htps:/]+github.com/([\w\-_.]+)/([\w\-_.]+)", re.MULTILINE)
        return url_re.findall(r.text)
    else:
        print('{}/{} not found'.format(user, repo))


def parse_fork_repos(json_results=RESULTS_JSON):
    fork_repos = []
    with open(json_results) as f:
        for repo in parse_scrapy_json(f.readlines()):
            if 'fork_commits' in repo:
                forked_repo = {
                    'name': repo['name'],
                    'user': repo['user'],
                    'branch': repo['branch'],
                    'last_updated': repo.get('last_updated'),
                    '+': 0, '-': 0
                }
                for c in repo['fork_commits']:
                    forked_repo['+' if c[1] == 'ahead' else '-'] = c[0]
                fork_repos.append(forked_repo)
    return fork_repos


def parse_repo_stars(json_results=RESULTS_JSON):
    repo_stars = []
    with open(json_results) as f:
        for repo in parse_scrapy_json(f.readlines()):
            repo_stars.append(repo)
    return repo_stars


def print_fork_repos(fork_repos):
    rows = []
    for repo in sorted(fork_repos, key=lambda k: int(k.get('+', 0)), reverse=True):
        rows.append([repo['branch'],
                     '+%s' % repo['+'],
                     '-%s' % repo['-'],
                     'https://{}/{}/{}'.format(GITHUB, repo['user'], repo['name']),
                     repo['last_updated'],
                     ])
    print(tabulate(rows, headers=['branch', 'ahead', 'behind', 'url', 'last_updated']))


def print_repos_stars(repos_stars):
    rows = []
    for repo in sorted(repos_stars, key=lambda k: int(k.get('stars', 0)), reverse=True):
        rows.append(['https://{}/{}/{}'.format(GITHUB, repo['user'], repo['name']),
                     repo['stars'],
                     repo.get('watchers'),
                     repo.get('contributors'),
                     repo.get('forks'),
                     repo.get('last_updated'),
                     ])
    print(tabulate(rows, headers=['url', 'stars', 'watchers', 'contributors', 'forks', 'last_updated']))


if __name__ == '__main__':
    args = docopt(__doc__, version='0.1')

    if (args['forks'] or args['stars']) and (not args['<user>'] or not args['<repo>']):
        print('Needs user and repo')
    else:
        if args['forks']:
            forks()
        elif args['parse_forks']:
            print_fork_repos(parse_fork_repos())
        elif args['stars']:
            stars()
        elif args['parse_stars']:
            print_repos_stars(parse_repo_stars())
        else:
            print('Command not found')
