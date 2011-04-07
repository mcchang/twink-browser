# taken from https://github.com/kzk/async-python-twitter/blob/master/twitter.py
import urllib

def Encode(s):
  # TODO: input_encoding?
  # if self._input_encoding:
  #   return unicode(s, self._input_encoding).encode('utf-8')
  # else:
  #   return unicode(s).encode('utf-8')
  return unicode(s).encode('utf-8')

def EncodePostData(post_data):
  if post_data is None:
    return None
  else:
    return urllib.urlencode(dict([(k, Encode(v)) for k, v in post_data.items()]))
