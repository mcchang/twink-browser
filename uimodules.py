"""Implements UI Module rendering handlers"""

import tornado.web

class Tweet(tornado.web.UIModule):
    def render(self, tweet):
        return self.render_string("modules/tweet.html", tweet=tweet)

class Link(tornado.web.UIModule):
    def render(self, link):
        return self.render_string("modules/link.html", link=link)
