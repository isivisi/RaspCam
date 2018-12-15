#import cv2              # opencv-python package
import socket
import io
import time
import threading
import raspcam.database

# for debugging without a raspberry pi
NON_PI = False
try:
	import picamera
except:
	NON_PI = True

class Camera:
    def __init__(self, type):
        self.type = type
        self.resolution = (480, 270)
        self.framerate = 30
        self.loopSpeed = 1 / self.framerate
        self.format = 'h264'
        self.lastStream = io.BytesIO()

    def startRecord(self, fileName):
        raise NotImplementedError("Cannot call abstract method")

    def stopRecord(self):
        raise NotImplementedError("Cannot call abstract method")

    def set(self, key, value):
        raise NotImplementedError("Cannot call abstract method")

    def getImage(self, file):
        raise NotImplementedError("Cannot call abstract method")

    def streamCamera(self, file):
        raise NotImplementedError("Cannot call abstract method")

class PICam(Camera):
    def __init__(self):
        super().__init__("pi")
        startT = time.time()
        self.camera = picamera.PiCamera()
        print ("Camera initialized in %s" % str(time.time() - startT))
        #self.camera.resolution = self.resolution

        # set saved settings
        camSettings = raspcam.database.getCameras(local=True)[0]
        self.camera.rotation = camSettings.rotation

        # Begin camera loop
        if not NON_PI:
            threading.Thread(target=self.getImageLoop).start()

    def getImage(self):
        stream = io.BytesIO()
        if not NON_PI:
            self.camera.capture(stream, format='jpeg', use_video_port=True)
        return stream

    def getImageLoop(self):
        while 1:
            try:
                self.lastStream = self.getImage()
                time.sleep(self.loopSpeed)
            except RuntimeError as e:
                print(e.message)
            except:
                print("Error in getcamera")

    #def streamImage(self, file):
    #    stream = io.BytesIO()
    #    for foo in self.camera.capture_continuous(stream, format='jpeg', use_video_port=True):
    #        stream.truncate()
    #        stream.seek(0)
    #        with open(file, 'wb') as w:
    #            w.write(stream.read())

    def startRecord(self, fileName):
        self.camera.start_recording(fileName)

    def stopRecord(self):
        self.camera.stop_recording()

    def streamCamera(self):
        self.camera.startRecord(self.stream, format=self.format, quality=23)

    def __del__(self):
        if not NON_PI:
            self.camera.close()
            print("Camera closed properly")
