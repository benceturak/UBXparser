import sys
import traceback

sys.path.append("/home/bence/data/UBXparser/src")

import UBXparser
from UBXmessage import *
import numpy as np

import getopt
#import importlib
#from scipy.interpolate import griddata
import logging
opts, args = getopt.getopt(sys.argv[1:], 'i:o:m:h:', ['input=', 'output=', 'messages', 'help'])
stations = None


checkMessages = (UBX,)
for o, v in opts:
    if o == '--input' or o == "-i":
        input = v
    elif o == '--output' or o == '-o':
        output = v
    elif o == '--messages' or o == '-m':
        checkMessages = (eval("("+v+")"))
    elif  o == '--help' or o == '-h':
        print("Usage:")

fid = open(input, 'br')


logging.basicConfig(filename="ttttttt.log", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


parser = UBXparser.UBXparser(fid)

msgs = {}
i = 0
for msg in parser.readFile():
    if not isinstance(msg, checkMessages):
        continue
    try:
        msgs[msg.__class__.__name__].append(msg)
    except:
        msgs[msg.__class__.__name__] = [msg,]

e = 0

fid = open(output, 'a')
for name, msg in msgs.items():
    for m in msg:
        i += 1
        if isinstance(m, UBX_CUS_ID):
            continue
        diff = round(m.getEpoch() - e)
        e = m.getEpoch()
        #print("{:7.0f}|{:.0f}".format(e, diff))
        #print(diff)
        print("{:7.0f}|{:.0f}|{:s}".format(e, diff,m.__class__.__name__), file=fid)
        #if isinstance(m, UBX_NAV_TIMEGPS):
            #print(m.data)
        #if i == 500:break
    print(name, len(msg))
        #try:
        #    if isinstance(msg, UBXmessage.UBX_NAV_HPPOSLLH):
        #        print(msg.data)
        #except Exception as err:
        #    print(err)
        #print(msg.data)
        #print(type(msg))
        #for i in msg.measurements:
        #    print(i)
