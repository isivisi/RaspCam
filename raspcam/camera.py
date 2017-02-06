import picamera
import cv2              # opencv-python package
import socket

class Camera:
    def __init__(self, type):
        self.type = type
        self.resolution = (320, 240)
        self.framerate = 30
        self.format = 'h264'

    def streamCamera(self, port):
        raise NotImplementedError("Cannot call abstract method")

    def set(self, key, value):
        raise NotImplementedError("Cannot call abstract method")

    def getImage(self, file):
        raise NotImplementedError("Cannot call abstract method")

class PICam(Camera):
    def __init__(self):
        def __init__(self):
            super().__init__("pi")
            picamera.PiCamera.resolution(self.resolution)
            picamera.PiCamera.framerate(self.framerate)

    def getImage(self, file):
        return picamera.PiCamera.capture(format='png', use_video_port=True, resize=self.resolution)

    def streamCamera(self, port):
        ssock = socket.socket()
        ssock.bind(('0.0.0.0', port))
        ssock.listen(0)

        while True:
            connectionAsFile = ssock.accept()[0].makefile("wb")
            try:
                picamera.PiCamera.start_recording(connectionAsFile, format=self.format)
            finally:
                connectionAsFile.close()
                ssock.close()