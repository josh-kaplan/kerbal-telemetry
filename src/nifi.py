import requests

class NiFi:
    def __init__(self, url):
        self.url = url

    def put(self, doc):
        r = requests.put(self.url, json=doc)
        return r
