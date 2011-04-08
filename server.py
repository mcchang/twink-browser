import base64
import constants
import os
import tornado.auth
import tornado.database
import tornado.httpclient
import tornado.ioloop
import tornado.web
import urlparse
import uuid

PORT = 8080

settings = {
  "static_path": os.path.join(os.path.dirname(__file__), "static"),
  "twitter_consumer_key": constants.TWITTER_CONSUMER_KEY,
  "twitter_consumer_secret": constants.TWITTER_CONSUMER_SECRET,
  "cookie_secret": base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
  "xsrf_cookies": True,
  "debug": True
}

class BaseHandler(tornado.web.RequestHandler):
  def get_current_user(self):
    return self.get_secure_cookie("user")

class MainHandler(BaseHandler):
  def get(self):
    if not self.current_user:
      self.render("main.html", api_key=constants.TWITTER_API_KEY)
      return
    name = tornado.escape.xhtml_escape(self.current_user)
    self.write("Hello, " + name)

class AuthenticationHandler(BaseHandler,
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
    # print user["username"]
    # print user["access_token"]
    access_token = user["access_token"]
    db = tornado.database.Connection("localhost", "twink-browser", user=constants.MYSQL_USER, password=constants.MYSQL_PASSWORD)
    if not db.get("SELECT * FROM users WHERE user='%s'" % user["username"]):
      db.execute("INSERT INTO users VALUES ('%s', '%s', '%s', '%s')" % (access_token["screen_name"],
                                                                        access_token["user_id"],
                                                                        access_token["key"],
                                                                        access_token["secret"]
                                                                       ))
    db.close()
    self.set_secure_cookie("user", user["username"])
    self.redirect('/')

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

