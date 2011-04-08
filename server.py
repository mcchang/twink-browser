import constants
import oauth2 as oauth
import os
import tornado.auth
import tornado.httpclient
import tornado.ioloop
import tornado.web
import twitter
import urlparse

PORT = 8080

settings = {
  "static_path": os.path.join(os.path.dirname(__file__), "static"),
  "twitter_consumer_key": constants.TWITTER_CONSUMER_KEY,
  "twitter_consumer_secret": constants.TWITTER_CONSUMER_SECRET,
  "debug": True
}

class MainHandler(tornado.web.RequestHandler):
  def get(self):
    print "GET"
    self.render("main.html", api_key=constants.TWITTER_API_KEY)

class AuthenticationHandler(tornado.web.RequestHandler,
                            tornado.auth.TwitterMixin):
  @tornado.web.asynchronous
  def get(self):
    if self.get_argument("oauth_token", None):
      self.get_authenticated_user(self.async_callback(self._on_auth))
      return
    self.authorize_redirect()

  def _on_auth(self, user):
    if not user:
      raise tornado.web.HTTPError(500, "Twitter auth failed")
    print user["username"]
    print user["access_token"]
    self.redirect('/')
    api = twitter.Api(consumer_key=constants.TWITTER_CONSUMER_KEY,
                      consumer_secret=constants.TWITTER_CONSUMER_SECRET,
                      access_token_key=user["access_token"]["key"],
                      access_token_secret=user["access_token"]["secret"])
    print api.VerifyCredentials()

class DisplayHandler(tornado.web.RequestHandler):
  def get(self):
    print "DISPLAY"

application = tornado.web.Application([
  (r"/", MainHandler),
  (r"/authenticate", AuthenticationHandler),
  (r"/display", DisplayHandler)
], **settings)

if __name__ == "__main__":
  application.listen(PORT)
  tornado.ioloop.IOLoop.instance().start()

