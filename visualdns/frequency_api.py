import os
import router
import settings
import tornado.web
import tornado.ioloop

if __name__ == "__main__":
    application = tornado.web.Application( 
        router.router, 
        **settings.settings
    )
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()