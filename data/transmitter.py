import socket
import numpy

HOST = "pixel.local"
PORT = 9999
WIDTH = 512
HEIGHT = 64
PACKET_SIZE = 49153

class Transmitter(object):

    def __init__(self):
        self.buffer = numpy.zeros(PACKET_SIZE, numpy.uint8)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_SNDBUF,49153)

    def send(self, data, offset):
        self.buffer[0] = 0
        idx = 0
        wx = 0
       
        for y in xrange(0,32):
            for x in xrange(0,512):
                wx = (x+offset)%512
                idx = (y*512+wx)*3
                self.buffer[idx+1] = data[y][x] >> 8 & 0xFF 
                self.buffer[idx+2] = data[y][x] >> 16 & 0xFF
                self.buffer[idx+3] = data[y][x] >> 24 & 0xFF

        self.sock.sendto(self.buffer,(HOST,PORT))
        
        self.buffer[0] = 1
        for y in xrange(32,64):
            for x in xrange(0,512):
                wx = (x+offset)%512
                idx = ((y-32)*512+wx)*3
                self.buffer[idx+1] = data[y][x] >> 8 & 0xFF 
                self.buffer[idx+2] = data[y][x] >> 16 & 0xFF
                self.buffer[idx+3] = data[y][x] >> 24 & 0xFF

        self.sock.sendto(self.buffer,(HOST,PORT))



