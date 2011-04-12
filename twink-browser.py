"""Implements main twink-browser server loop"""

import os
import tornado.auth
import tornado.database
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import ttp
import uimodules
import urllib

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)
define("mysql_host", default="127.0.0.1:3306",
        help="twink-browser database host")
define("mysql_database", default="database",
        help="twink-browser database name")
define("mysql_user", default="user", help="twink-browser database user")
define("mysql_password", default="password",
        help="twink-browser database password")
define("twitter_consumer_key", default="consumer_key",
        help="twink-browser twitter consumer key")
define("twitter_consumer_secret", default="consumer_secret",
        help="twink-browser twitter consumer secret")
define("twitter_api_key", default="api_key",
        help="twink-browser twitter api key")
define("cookie_secret", default="cookie secret",
        help="twink-browser cookie secret")


class Application(tornado.web.Application):
    """
    Initialize tornado Application with handlers and settings
    Starts global database as well.
    """
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
            ui_modules=uimodules,
            xsrf_cookies=True,
            debug=True
        )
        tornado.web.Application.__init__(self, handlers, **settings)

        # Global DB connection
        self.database = tornado.database.Connection(options.mysql_host,
                                              options.mysql_database,
                                              user=options.mysql_user,
                                              password=options.mysql_password)


class BaseHandler(tornado.web.RequestHandler):
    @property
    def database(self):
        return self.application.database

    def get_current_user(self):
        user = self.get_secure_cookie("user")
        if not user:
            return None
        return self.database.get("SELECT * FROM users WHERE user='%s'" % user)

    def get_current_user_access(self):
        if not self.current_user:
            return None
        _current_user = self.current_user
        return dict(username=_current_user["user"],
                    user_id=_current_user["user_id"],
                    key=_current_user["access_key"],
                    secret=_current_user["access_secret"])


class MainHandler(BaseHandler, tornado.auth.TwitterMixin):
    @tornado.web.asynchronous
    def get(self):
        if not self.current_user:
            self.render("main.html",
                        api_key=options.twitter_api_key,
                        links=None)
            return
        self.twitter_request(path = "/statuses/friends_timeline",
                             access_token = self.get_current_user_access(),
                             callback = self.async_callback(self.show_tweets),
                             count = 200)

    def show_tweets(self, tweets):
        p = ttp.Parser()
        links = []
        for tweet in tweets:
            result = p.parse(tweet["text"])
            if result.urls:
                # print result.urls 
                links.append(result.urls[0])
                # print links
        self.render("main.html",
                    api_key = options.twitter_api_key,
                    links = links if links else None)


class AuthenticationHandler(BaseHandler, tornado.auth.TwitterMixin):
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
        if not self.database.get("SELECT * FROM users WHERE user='%s'" %
                           user["username"]):
            self.database.execute(
                    "INSERT INTO users (user, user_id, access_key,"
                    "access_secret) VALUES ('%s', '%s', '%s', '%s')" %
                    (access_token["screen_name"], access_token["user_id"],
                     access_token["key"], access_token["secret"]))
        self.set_secure_cookie("user", user["username"])
        self.redirect('/')


class DisplayHandler(tornado.web.RequestHandler):
    # TODO: do these need to be authenticated?
    def get(self):
        print "DISPLAY_GET"

    def post(self):
        print "DISPLAY_POST"
        url = self.get_argument("url")
        print url
        sock = urllib.urlopen(url)
        html = sock.read()
        sock.close()
        print html
        self.write(html)


def main():
    """Initialize config options and start server."""
    tornado.options.parse_config_file("server.conf")
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
