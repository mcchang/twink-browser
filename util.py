# taken from https://github.com/kzk/async-python-twitter/blob/master/twitter.py
import constants
import oauth2 as oauth
import os
import sys
import urllib

CALLBACK_URL       = 'http://127.0.0.1:8080/authenticated'
REQUEST_TOKEN_URL  = 'https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL   = 'https://api.twitter.com/oauth/access_token'
AUTHENTICATION_URL = 'https://api.twitter.com/oauth/authenticate'
# parse_qsl moved to urlparse module in v2.6
try:
  from urlparse import parse_qsl
except:
  from cgi import parse_qsl

class TwitterOAuthConnector:
  def __init__(self, input_encoding=None):
    self.token = None
    self.oauth_consumer = oauth.Consumer(key=constants.TWITTER_CONSUMER_KEY,
                                         secret=constants.TWITTER_CONSUMER_SECRET)
    self._input_encoding = input_encoding

  def _Encode(self, s):
    if self._input_encoding:
      return unicode(s, self._input_encoding).encode('utf-8')
    else:
      return unicode(s).encode('utf-8')

  def _EncodePostData(self, post_data):
    if post_data is None:
      return None
    else:
      return urllib.urlencode(dict([(k, Encode(v)) for k, v in post_data.items()]))

  def GetAuthenticationURL(self):
    oauth_client = oauth.Client(self.oauth_consumer)
    resp, content = oauth_client.request(REQUEST_TOKEN_URL, 
                                         method="GET",
                                         parameters={'oauth_callback': _Encode(CALLBACK_URL)})

    if resp['status'] != '200':
      print 'Invalid response from Twitter requesting temp token: %s' % resp['status']
    else:
      request_token = dict(parse_qsl(content))
      print request_token
      self.token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
      oauth_client = oauth.Client(oauth_consumer, self.token)
      return '%s?oauth_token=%s' % (AUTHENTICATION_URL, request_token['oauth_token'])

  def GetAccessToken(self, oauth_verifier):
    self.token.set_verifier(oauth_verifier)
    oauth_client = oauth.Client(self.oauth_consumer, self.token)
    resp, content = client.request(ACCESS_TOKEN_URL, method="POST")
    access_token = dict(parse_qsl(content))
    print access_token


