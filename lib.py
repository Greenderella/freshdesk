import re
import requests as r
from decouple import config

class FreshdeskIterator:
  def __init__(self, url):
    self.url = url

  def __iter__(self):
    self.memory = []
    self.count = 1
    return self

  def __next__(self):
    if not self.memory:
        if self.count == 1:
            desk = 'https://bitwarden.freshdesk.com'
            self.query = r.get(desk + self.url, auth=(config('API_KEY'), 'X')) 
        else:
            try:
                self.query.headers['link']
            except:
                raise StopIteration
            else:
                l = re.search(r'<(.*?)>', self.query.headers['link']).group(1) 
                self.query = r.get(l, auth=(config('API_KEY'), 'X'))
        print('.', end='', flush=True)
        self.memory = self.query.json()
        self.count += 1
    if not self.memory:
        raise StopIteration
    return self.memory.pop()