# -*- coding: utf-8 -*-
import json
from tabulate import tabulate

FORK_JSON = '.json'

forks = []
with open(FORK_JSON) as f:
    j = json.load(f)
    print(len(j))
    for o in j:
        plus = minus = None
        for c in o.get('commits', []):
            if c[1] == 'ahead': plus = c[0]
            if c[1] == 'behind': minus = c[0]
        if plus: o['+'] = plus
        if minus: o['-'] = minus
        forks.append(o)

rows = []
for fk in sorted(forks, key=lambda k: int(k.get('+', 0)), reverse=True):
    rows.append([fk['branch'],
                 '+%s' % fk.get('+', 0),
                 '-%s' % fk.get('-', 0),
                 'https://github.com/%s/%s' % (fk['user'], fk['repo']),
                 fk.get('update_date'),
                 ])
print(tabulate(rows, headers=['branch', 'ahead', 'behind', 'url', 'update_date']))
