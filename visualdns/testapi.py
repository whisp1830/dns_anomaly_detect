import os
import json
import tornado.web
import tornado.ioloop

class TestHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        res = {
            "key": [1,2,3],
            "value" : [4,5,6]
        }
        self.write(json.dumps(res))
        self.finish()

    def post(self):
        self.write("hello , ADD\n")

    def put(self):
        self.write("hello , UPDATE\n")

    def delete(self):
        self.write("hello , DELETE\n")


if __name__ == "__main__":
    settings = {
        'debug' : True,
        'static_path' : os.path.join(os.path.dirname(__file__) , "static") ,
        'template_path' : os.path.join(os.path.dirname(__file__) , "template") ,
    }

    application = tornado.web.Application([
        (r"/" , MainHandler),
        (r"/index", TestHandler)
    ] , **settings)
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()