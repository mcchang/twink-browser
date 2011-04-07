import constants
import oauth2 as oauth
import os
import tornado.httpclient
import tornado.ioloop
import tornado.web
import twitter
import urlparse
import util

PORT = 8080

settings = {
  "static_path": os.path.join(os.path.dirname(__file__), "static"),
  "debug": True
}

class MainHandler(tornado.web.RequestHandler):
  def get(self):
    print "GET"
    # self.write("Hello, world")
    self.render("main.html", api_key=constants.TWITTER_API_KEY)

  def post(self):
    print "POST"
    print self.request
    bridge_code = self.get_argument("bridge_code")

    client = tornado.httpclient.HTTPClient()
    body = util.EncodePostData({'oauth_bridge_code': bridge_code})
    print "BODY: ", body
    consumer = oauth.Consumer(key=constants.TWITTER_CONSUMER_KEY,
                              secret=constants.TWITTER_CONSUMER_SECRET)
    access_token_url = "https://api.twitter.com/oauth/access_token"
    client = oauth.Client(consumer)
    resp, content = client.request(access_token_url, method="POST", body=body)
    # TODO check response to see if its 404 or something
    print "RESP: ", resp
    print "CONTENT: ", content
    # content = content.split('&')
    # pair =dict([(pair.split('=')[0], pair.split('=')[1]) for pair in content.split('&')])
    content = urlparse.parse_qs(content)
    content = dict([(k, v[0]) for k, v in content.items()])
    print content
    api = twitter.Api(consumer_key=constants.TWITTER_CONSUMER_KEY,
                      consumer_secret=constants.TWITTER_CONSUMER_SECRET,
                      access_token_key=content["oauth_token"],
                      access_token_secret=content["oauth_token_secret"])
    print api.VerifyCredentials()

    # request = tornado.httpclient.HTTPRequest("https://api.twitter.com/oauth/access_token", method="POST", body=body)
    # try:
    #   response = client.fetch(request)
    #   print "FETCHED RESPONSE"
    #   print response.body
    # except tornado.httpclient.HTTPError, e:
    #   print "ERROR: ", e



application = tornado.web.Application([
  (r"/", MainHandler),
], **settings)

if __name__ == "__main__":
  application.listen(PORT)
  tornado.ioloop.IOLoop.instance().start()

