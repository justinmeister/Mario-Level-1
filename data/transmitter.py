import threading
import socket
import numpy
import time

HOST = "localhost"
PORT = 9999
WIDTH = 512
HEIGHT = 64
PACKET_SIZE = 49153

class Transmitter(threading.Thread):

    def __init__(self,q):
        self.sendbuf = numpy.zeros(PACKET_SIZE, numpy.uint8)
        self.q = q
        self.buffers = [ None, None, None ]
        self.sending = 0
        self.drawing = 1
        self.frames = 0
        self.stime = time.time()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_SNDBUF,49153)
        self.lock = threading.Lock()
        threading.Thread.__init__(self)
        self.setDaemon(True)

    def incdrawing(self):
        self.lock.acquire()
        for x in xrange(0,3):
            if (self.drawing != x and self.sending != x):
                self.drawing = x
                break
        self.lock.release()

    def incsending(self):
        self.lock.acquire()
        for x in xrange(0,3):
            if (self.drawing != x and self.sending != x):
                self.sending = x
                break
        self.lock.release()

    def queue(self, data, offset):
        if (self.q.empty()):
            self.q.put({ "data":data, "offset":offset })

    def dequeue(self):
        a = self.q.get()

        self.incdrawing()

        self.buffers[self.drawing] = { "sent": False, "data": a["data"], "offset": a["offset"] }

    def send(self):
        self.incsending()

        ## If we haven't drawn the first frame yet then it's still None
        if (self.buffers[self.sending] == None):
            return False

        buf = self.buffers[self.sending]["data"]
        offset = self.buffers[self.sending]["offset"]

        if (self.buffers[self.sending]["sent"]):
            return False

        self.sendbuf[0] = 0
        idx = 0
        wx = 0
        c = 0
      
        for y in xrange(0,32):
            for x in xrange(0,512):
                wx = (x+offset)%512
                idx = (y*512+wx)*3
                self.sendbuf[idx+1] = buf[x][y][0]
                self.sendbuf[idx+2] = buf[x][y][1]
                self.sendbuf[idx+3] = buf[x][y][2]
        
        self.sock.sendto(self.sendbuf,(HOST,PORT))
       
        self.sendbuf[0] = 1

        for y in xrange(32,64):
            for x in xrange(0,512):
                wx = (x+offset)%512
                idx = ((y-32)*512+wx)*3
                self.sendbuf[idx+1] = buf[x][y][0]
                self.sendbuf[idx+2] = buf[x][y][1]
                self.sendbuf[idx+3] = buf[x][y][2]

        self.sock.sendto(self.sendbuf,(HOST,PORT))

        self.buffers[self.sending]["sent"] = True

        self.frames = self.frames + 1
        if (self.frames % 10 == 0):
            t = time.time()
            print "Transmit FPS = {:.2f}".format(self.frames/(t-self.stime))
            

        return True

    def run(self):
        while(True):
            if (not self.send()):
                print "Send failed.  Sleep"
                time.sleep(0.1)

