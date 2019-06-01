# -*- coding: utf-8 -*-
"""
Usage:
    proc.py forks <user> <repo>
    proc.py proc_forks [--file=JSON_RESULTS]
    proc.py stars <user> <repo>
    proc.py -h | --help | --version

Options:
    --file=JSON_RESULTS  JSON file with results from spider [default: results.json]
"""
import json
import requests

from docopt import docopt
from parsel import Selector
from scrapy import cmdline
from tabulate import tabulate

GITHUB = 'github.com'
FORKS_URL = 'network/members'
RESULTS_JSON = 'results.json'

cmd = ["scrapy", "crawl", "repo", "-a"]


def get_forks_urls(user, repo):
    r = requests.get('https://{}/{}/{}/{}'.format(GITHUB, user, repo, FORKS_URL))
    if r.status_code == 200:
        sel = Selector(text=r.text)
        return sel.css('.repo a:last-child::attr(href)').getall()
    else:
        print('{}/{} not found'.format(user, repo))


def forks():
    cmd.append('user_repos=' + ';'.join(get_forks_urls(args['<user>'], args['<repo>'])))
    try:
        cmdline.execute(cmd)
    except BaseException:
        pass

    proc_forks()


def proc_forks(json_results=RESULTS_JSON):
    forks_commits = []
    with open(json_results) as f:
        for l in f.readlines():
            j = json.loads(l)
            plus = minus = None
            for c in j.get('fork_commits', []):
                if c[1] == 'ahead': plus = c[0]
                if c[1] == 'behind': minus = c[0]
            if plus: j['+'] = plus
            if minus: j['-'] = minus
            forks_commits.append(j)
    rows = []
    for fk in sorted(forks_commits, key=lambda k: int(k.get('+', 0)), reverse=True):
        rows.append([fk['branch'],
                     '+%s' % fk.get('+', 0),
                     '-%s' % fk.get('-', 0),
                     'https://%s/%s/%s' % (GITHUB, fk['user'], fk['name']),
                     fk.get('last_updated'),
                     ])
    print(tabulate(rows, headers=['branch', 'ahead', 'behind', 'url', 'last_updated']))


# TODO
def stars():
    pass


if __name__ == '__main__':
    args = docopt(__doc__, version='0.1')

    if (args['forks'] or args['stars']) and (not args['<user>'] or not args['<repo>']):
        print('Needs user and repo')
    else:
        if args['forks']:
            forks()
        elif args['proc_forks']:
            proc_forks(args['--file'])
        elif args['stars']:
            stars()
        else:
            print('Command not found')
