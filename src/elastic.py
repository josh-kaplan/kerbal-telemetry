
import datetime
import json
import os
import ssl
import time
from elasticsearch import Elasticsearch


def make_ssl_context():
    """Create an SSL context for the Elasticsearch client.

    NOTE: This should only be needed if the Elasticsearch server is running with 
    SSL enabled and using a self-signed certificate. Which is not the case for
    our default configuration.
    """
    __dirname__ = os.path.abspath(os.path.dirname(__file__))
    cert_path = os.path.abspath(os.path.join(__dirname__, '..', 'data', 'http_ca.crt'))
    print(cert_path)
    context = ssl.create_default_context(cafile=cert_path)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context


class Elastic:
    def __init__(self, index, delete_index=False):
        self.index = index
        self.es = self.connect()
        if delete_index:
            self.delete_index()

    def connect(self):
        es = Elasticsearch(
            "http://localhost:9200", 
            basic_auth=("elastic", "changeme"),
            #ssl_context=make_ssl_context()
        )
        #print("Status: ", es.ping())
        return es

    def delete_index(self):
        try:
            print('Deleting index ...')
            resp = self.es.indices.delete(index=self.index, ignore=[400, 404])
            print(resp)
        except:
            print("Something went wrong during delete. But it's okay.")

    def put(self, doc):
        doc['@timestamp'] = datetime.datetime.utcnow()
        resp = self.es.index(index=self.index, document=doc)
        ok = resp.get('result', '') == 'created'
        if not ok:
            print(resp)

    def get_all(self, query):
        resp = self.es.search(index="test-index", query={"match_all": {}})
        print("Got %d Hits:" % resp['hits']['total']['value'])
        return resp['hits']['hits']
        

