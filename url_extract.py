from pyquery import PyQuery as pq
import re

def extract_bw_url(body):
    d=pq(body.replace(r'\"','"'))

    links_with_none = list(map(lambda a: a.attr("href"), d("a").items()))

    links = filter(None, links_with_none)

    return list(filter(lambda link: bool(re.match(r'^https?://bitwarden\.com/help', link)), links))
