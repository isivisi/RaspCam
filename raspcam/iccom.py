# Camera communication over the internet
# Used to send / receive information about cameras on a network

import socket

import sys
import time
import raspcam.database
import threading

class ICCom:
    def __init__(self, isHub, port):
        self.isHub = isHub
        self.port = port
        self.foundCameras = []
        self.foundHub = False

        self.localCam = raspcam.database.getCamera(raspcam.database.getSetting("localCamera"))

    def broadcast(self, msg):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(msg.encode('utf-8'), ('255.255.255.255', self.port))

    def listen(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((' ', self.port))
        print("Listening...")
        data = None
        while 1:
            return s.recvfrom(1024)

    def send(self, msg, host):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(msg.encode("utf-8"), (host, self.port))

    def beginCom(self):
        if self.isHub:
            # broadcast that we are the hub
            threading.Thread(target=self.getCameraLoop)
            while 1:
                data = self.listen()
                try:
                    cd = data.split(",")
                    camera = raspcam.models.Camera(cd[0], cd[1], cd[2], cd[3])
                    self.foundCamera.append(camera)
                    print("Camera found on network, adding to system")
                except:
                    print("Failed to gather camera information")

        else:
            print("Waiting for hub...")
            while 1:
                data = self.listen()
                if data[0] == "GETCAMERA":
                    #send camera data to hub asking for it
                    self.foundHub = True
                    self.send(str(self.localCam), data[1])
                    print("Found hub, sending camera data")

    def getCameraLoop(self):
        print("Beginning camera search...")
        while 1:
            time.sleep(5)
            self.broadcast("GETCAMERA")



