#import raspcam.camera
import threading
import time
import tornado
import tornado.ioloop
import tornado.web
import os

fileLocation = "liveFeed.png"
port = 8888

def main():
    #cam = raspcam.camera.PICam()
    #file =open(fileLocation, 'wb')
    #threading._start_new_thread(record, (cam, file,))

    app = make_app()
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()

def record(cam, file):
    while 1:
        cam.getImage(file);
        time.sleep(0.15) # 60 times a second

def make_app():
    settings= {
        "static_path": os.path.dirname(__file__),
    }

    return tornado.web.Application([
        (r"/", MainHandler),
    ], **settings)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("web/streamvideo.html")

main()