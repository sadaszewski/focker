from http.client import HTTPConnection, \
    HTTPSConnection
from urllib.parse import urlparse


def get(url, headers={}):
    url = urlparse(url)
    netloc = url.netloc.split(':')
    host = netloc[0]
    if url.scheme == 'https':
        conn = HTTPSConnection(netloc[0], netloc[1] \
            if len(netloc) > 1 else 443)
    else:
        conn = HTTPConnection(netloc[0], netloc[1] \
            if len(netloc) > 1 else 80)
    req = conn.request('GET', url.path + ('?' + url.query \
        if url.query else ''), headers=headers)
    resp = conn.getresponse()
    status, reason = resp.status, resp.reason
    if status == 200:
        return (status, reason, resp.read(), resp)
    else:
        return (status, reason, None, resp)


class RegistryClient(object):
    def __init__(self, url):
        self.url = url

    def authAnon(self):
        get(url)


def command_reg_search(args):
    raise NotImplementedError


def command_reg_tags(args):
    raise NotImplementedError


def command_reg_pull(args):
    raise NotImplementedError


def command_reg_push(args):
    raise NotImplementedError
