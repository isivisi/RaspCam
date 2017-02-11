# RaspCam
# A simple web controller for raspberry pi cameras.
# Written by John Iannandrea

import raspcam.camera
import raspcam.models
import raspcam.database
import raspcam.iccom
import threading
import time
import tornado
import tornado.ioloop
import tornado.web
import tornado.gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
import os
import uuid
import signal
import psutil           # for cpu info

try:
    cam = raspcam.camera.PICam()
except:
    cam = None
    print("Camera does not exist, have you enabled the pi camera using the raspi-config command?")
performLoop = True

# Create app
def main():
    port = int(database.getSetting("Port"))
    app = make_app()
    app.listen(port)
    print("Starting web application on port %s" % port)
    signal.signal(signal.SIGINT, signalHandler)
    tornado.ioloop.IOLoop.current().start()

# stop ioloop on shutdown
def signalHandler(signum, frame):
    global performLoop, cam
    tornado.ioloop.IOLoop.instance().stop()
    del(cam)
    performLoop = False
    print("RaspCam application shut down")
    exit()

# Describes the tornado webapp.
def make_app():
    settings= {
        "static_path": os.path.dirname(__file__),
        "cookie_secret": uuid.uuid4().hex
    }

    return tornado.web.Application([
        (r"/", MainHandler),
        (r'/login', LoginHandler),
        (r"/camera/(.*)", CameraHandler),
        (r"/settings", SettingsHandler),
        #(r'/feed/(.*)', tornado.web.StaticFileHandler, {'path': os.path.dirname(__file__) + '/feed'}),
        (r'/feed/.*', FeedHandler),
        (r'/system/', SystemHandler),
        ('/firststart/(.*)', firstStartHandler)
    ], **settings)

class firstStartHandler(tornado.web.RequestHandler):
    def get(self, page):
        if page == 'ishub':
            database.changeSetting("Hub", "1")
            database.changeSetting("firstStart", "0")
        elif page == "isextra":
            database.changeSetting("Hub", "0")
            database.changeSetting("firstStart", "0")
        else:
            self.render('web/firststart.html')
            return
        self.redirect('/camera/')

# Handles the main webpage
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        # Make sure the user is logged in
        #if not self.get_secure_cookie("user"):
        #    self.redirect("/login")
        #    return

        if database.getSetting("firstStart") == "1":
            self.redirect("/firststart/")
        elif database.getSetting("Hub") == "1":
            # grab camera details and split them into arrays of two for visual purposes
            cameras = database.getCameras()
            cameras = [cameras[i:i + 2] for i in range(0, len(cameras), 2)]
            self.render("web/index.html", cameras=cameras)

# Specific camera view
class CameraHandler(tornado.web.RequestHandler):
    def get(self, page):
        if page == "new" and database.getSetting("Hub") == "1":
            self.render('web/newcamera.html')
        else:
            self.render("web/camera.html")

    def post(self, page):
        if database.getSetting("Hub") == "1":
            camName = self.get_argument("cameraName")
            ip = self.get_argument("ip")
            port = self.get_argument("port")

            if camName and ip and port:
                location = '%s:%s/feed/' % (ip, port,)
                database.createCamera(camName, location, 0, str(uuid.uuid4()))
                print("New camera location added")
                self.redirect('/')
                return
            self.redirect("/camera/new")

# Handles login page and sets up session
class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        if database.getSetting("Hub") == "1":
            self.render("web/login.html")

    def post(self):
        if database.getSetting("Hub") == "1":
            username = self.get_argument("username")
            password = self.get_argument("password")
            if username != "" and password != "":
                #If user information was correct give them a secure cookie so we can identify what user they are later.
                if raspcam.database.userCheck(username, password):
                    self.set_secure_cookie("user", username)
                    print("Login successful for user %s" % username)
                    self.redirect("/")
                    return
            print("Failed login attempt for user %s" % username)
            self.redirect("/login")

class SettingsHandler(tornado.web.RequestHandler):
    def get(self):
        if database.getSetting("Hub") == "1":
            if self.get_secure_cookie("user"):
                userInfo = database.getUser(self.get_secure_cookie("user").decode("utf-8"))
                # Only serve settings page to admin users
                if userInfo and userInfo.isAdmin:
                    settings = database.getSettings()
                    self.render("web/settings.html", settings=settings)
                    return
            self.redirect("/login")

    def post(self):
        if database.getSetting("Hub") == "1":
            if self.get_secure_cookie("user"):
                userInfo = database.getUser(self.get_secure_cookie("user").decode("utf-8"))
                # Only change settings if user is admin
                if userInfo and userInfo.isAdmin:
                    for arg in self.request.arguments.keys():
                        database.changeSetting(arg, self.request.arguments[arg][0].decode("utf-8"))
                    self.redirect('/')
                    return
            self.redirect('/login')

class SystemHandler(tornado.web.RequestHandler):
    def get(self):
        ram = format(float(psutil.virtual_memory().used / psutil.virtual_memory().total), '.2f')
        text = "cpu: %s ram: %s" % (psutil.cpu_percent(), ram)
        self.set_header('Content-length', len(text))
        self.write(text)

# Grab image from camera upon request
class FeedHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=16)

    @run_on_executor
    def runGetCam(self):
        return cam.lastStream.getvalue()

    @tornado.gen.coroutine
    def get(self):
        # returns the image in bytes
        if cam:
            bytes = yield self.runGetCam()
            # setup headers so the webbrowser know how to deal with our data
            self.set_header('Content-type', 'image/jpg')
            self.set_header('Content-length', len(bytes))
            self.write(bytes)
            self.finish()
            return
        self.write("Camera not available")
        self.finish()

main()