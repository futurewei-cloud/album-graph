# -*- coding:utf-8 -*-

import urllib2
import json
import ssl
from urllib2 import HTTPError, URLError
import signer
import ais


#
# access asr, asr_bgm,post data by token
#
def asr_bgm(token, url):
    _url = 'https://%s/v1.0/bgm/recognition' % ais.AisEndpoint.ENDPOINT

    _data = {
        "url": url,
    }

    kreq = urllib2.Request(url=_url)
    kreq.add_header('Content-Type', 'application/json')
    kreq.add_header('X-Auth-Token', token)
    kreq.add_data(json.dumps(_data))

    resp = None
    status_code = None
    try:
        #
        # Here we use the unvertified-ssl-context, Because in FunctionStage
        # the client CA-validation have some problem, so we must do this.
        #
        _context = ssl._create_unverified_context()
        r = urllib2.urlopen(kreq, context=_context)

    #
    # We use HTTPError and URLError，because urllib2 can't process the 4XX &
    # 500 error in the single urlopen function.
    #
    # If you use a modern, high-level designed HTTP client lib, Yeah, I mean requests,
    # there is no this problem.
    #
    except HTTPError, e:
        resp = e.read()
        status_code = e.code
    except URLError, e:
        resp = e.read()
        status_code = e.code
    else:
        status_code = r.code
        resp = r.read()
    return resp


#
# access asr, asr_bgm,post data by ak,sk
#
def asr_bgm_aksk(_ak, _sk, url):
    _url = 'https://%s/v1.0/bgm/recognition' % ais.AisEndpoint.ENDPOINT

    sig = signer.Signer()
    sig.AppKey = _ak
    sig.AppSecret = _sk
    _data = {
        "url": url,
    }

    kreq = signer.HttpRequest()
    kreq.scheme = "https"
    kreq.host = ais.AisEndpoint.ENDPOINT
    kreq.uri = "/v1.0/bgm/recognition"
    kreq.method = "POST"
    kreq.headers = {"Content-Type": "application/json"}
    kreq.body = json.dumps(_data)

    resp = None
    status_code = None
    try:
        sig.Sign(kreq)
        #
        # Here we use the unvertified-ssl-context, Because in FunctionStage
        # the client CA-validation have some problem, so we must do this.
        #
        _context = ssl._create_unverified_context()
        req = urllib2.Request(url=_url, data=kreq.body, headers=kreq.headers)
        resp = urllib2.urlopen(req, context=_context)
    #
    # We use HTTPError and URLError，because urllib2 can't process the 4XX &
    # 500 error in the single urlopen function.
    #
    # If you use a modern, high-level designed HTTP client lib, Yeah, I mean requests,
    # there is no this problem.
    #
    except HTTPError, e:
        resp = e.read()
        status_code = e.code
    except URLError, e:
        resp = e.read()

    return resp.read()
