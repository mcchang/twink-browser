import constants
import os
import tornado.ioloop
import tornado.web
import twitter

PORT = 8080

settings = {
  "static_path": os.path.join(os.path.dirname(__file__), "static"),
  "debug": True
}

class MainHandler(tornado.web.RequestHandler):
  def get(self):
    api = twitter.Api(consumer_key=constants.TWITTER_CONSUMER_KEY,
                      consumer_secret=constants.TWITTER_CONSUMER_SECRET,
                      access_token_key=constants.TWITTER_ACCESS_TOKEN,
                      access_token_secret=constants.TWITTER_ACCESS_TOKEN_SECRET)
    print api.VerifyCredentials()
    self.write("Hello, world")


application = tornado.web.Application([
  (r"/", MainHandler),
], **settings)

if __name__ == "__main__":
  application.listen(PORT)
  tornado.ioloop.IOLoop.instance().start()

