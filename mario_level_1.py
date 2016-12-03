#!/usr/bin/env python
__author__ = 'justinarmstrong'

"""
This is an attempt to recreate the first level of
Super Mario Bros for the NES.
"""

import sys
import pygame as pg
from data.main import main
import cProfile
from multiprocessing import Process,Queue
from data import transmitter

def childrun(queue):
    print "I'm the child."
    t = transmitter.Transmitter(queue)
    t.start()

    while (True):
        t.dequeue()

if __name__=='__main__':
    q = Queue()
    p = Process(target=childrun, args=(q,))
    p.start()

    main(q)
    p.join()
    pg.quit()
    sys.exit()
