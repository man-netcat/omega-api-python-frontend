import json
import os
from urllib.parse import urlencode

import requests_cache

if not os.path.exists('request_cache.sqlite'):
    requests_cache.install_cache('request_cache')
session = requests_cache.CachedSession('request_cache')

base_url = "https://web.duelistsunite.org/omega-api-decks/convert?%s"

omegalist = "M+c/+/cxq5HNGya7JYWM71T/sSx/vZgJhOVcAuDY1jaSBY59gpijeZuZQHh31BM4PvRZjhWG1yvfY4DhpRdMWNftuc8Iwz2NF1lg+PjnOQz85Wvg+MZcexYQvqUbx7D5yxmmjTXFLH2dHYznAtoYYvYbstjacTIefMXMfNjfkeGIiyJrddwHxkvSjoymW/axyMhEs+xo5GRWj1rCWJk1gWGVoCNTTnMn43Wp+YzO++4ywPDvOyKMahOcmGF47SMuJhiGqQdhAA=="


def scrape(list):
    dict = {'to': 'names', 'list': list}
    string = urlencode(dict)
    url = base_url % string
    response = session.get(url)
    if not response.ok:
        print(f"ERROR {response.status_code}: {url}")
        return None
    else:
        return response.json()


if __name__ == "__main__":
    result = scrape(omegalist)
    with open('output.json', 'w') as f:
        json.dump(result, f, indent=4, sort_keys=True)
