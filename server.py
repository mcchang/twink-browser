import os
import tornado.ioloop
import tornado.web

PORT = 8080

settings = {
  "static_path": os.path.join(os.path.dirname(__file__), "static"),
  "debug": True
}

class MainHandler(tornado.web.RequestHandler):
  def get(self):
    self.write("Hello, world")

application = tornado.web.Application([
  (r"/", MainHandler),
], **settings)

if __name__ == "__main__":
  application.listen(PORT)
  tornado.ioloop.IOLoop.instance().start()

