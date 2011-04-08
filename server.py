import base64
import constants
import os
import tornado.auth
import tornado.database
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import urlparse
import uuid

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)
define("mysql_host", default="127.0.0.1:3306", help="twink-browser database host")
define("mysql_database", default="database", help="twink-browser database name")
define("mysql_user", default="user", help="twink-browser database user")
define("mysql_password", default="password", help="twink-browser database password")
define("twitter_consumer_key", default="consumer_key", help="twink-browser twitter consumer key")
define("twitter_consumer_secret", default="consumer_secret", help="twink-browser twitter consumer secret")
define("twitter_api_key", default="api_key", help="twink-browser twitter api key")
define("cookie_secret", default="cookie secret", help="twink-browser cookie secret")

class Application(tornado.web.Application):
  def __init__(self):
    handlers = [
      (r"/", MainHandler),
      (r"/authenticate", AuthenticationHandler),
      (r"/display", DisplayHandler)
    ]
    settings = dict(
      static_path=os.path.join(os.path.dirname(__file__), "static"),
      template_path=os.path.join(os.path.dirname(__file__), "templates"),
      twitter_consumer_key=options.twitter_consumer_key,
      twitter_consumer_secret=options.twitter_consumer_secret,
      cookie_secret=options.cookie_secret,
      xsrf_cookies=True,
      debug=True
    )
    tornado.web.Application.__init__(self, handlers, **settings)

    # Global DB connection 
    self.db = tornado.database.Connection(options.mysql_host, 
                                          options.mysql_database, 
                                          user=options.mysql_user, 
                                          password=options.mysql_password)
    

class BaseHandler(tornado.web.RequestHandler):
  @property
  def db(self):
    return self.application.db

  def get_current_user(self):
    user = self.get_secure_cookie("user")
    if not user:
      return None
    return self.db.get("SELECT * FROM users WHERE user='%s'" % user)

class MainHandler(BaseHandler):
  def get(self):
    if not self.current_user:
      self.render("main.html", api_key=constants.TWITTER_API_KEY)
      return
    name = tornado.escape.xhtml_escape(self.current_user["user"])
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
    access_token = user["access_token"]
    if not self.db.get("SELECT * FROM users WHERE user='%s'" % user["username"]):
      self.db.execute("INSERT INTO users VALUES ('%s', '%s', '%s', '%s')" % (access_token["screen_name"],
                                                                        access_token["user_id"],
                                                                        access_token["key"],
                                                                        access_token["secret"]
                                                                       ))
    self.set_secure_cookie("user", user["username"])
    self.redirect('/')

class DisplayHandler(tornado.web.RequestHandler):
  def get(self):
    print "DISPLAY"

if __name__ == "__main__":
  tornado.options.parse_config_file("server.conf")
  tornado.options.parse_command_line()
  http_server = tornado.httpserver.HTTPServer(Application())
  http_server.listen(options.port)
  tornado.ioloop.IOLoop.instance().start()

