import _io
import queue
from UBXmessage import UBXmessage

class UBXparser(object):

    pream = b'\xB5\x62'

    def __init__(self, source):
        if isinstance(source, _io.BufferedReader):
            self.source = source
            self.sourceType = "file"
        elif isinstance(source, queue):
            pass
        else:
            raise Exception()
    def run(self):
        pass

    def readFile(self):
        bin = self.source.read()

        msg = b''
        for i in range(0, len(bin)):
            if bin[i:i+2] == self.pream and len(msg) != 0:
                #print(msg)
                UBXmsg = UBXmessage(bin=msg)
                #print(UBXmsg)

                msg = b''
            msg = msg + bin[i:i+1]


if __name__ == "__main__":
    fid = open("../proba.ubx", 'br')
    parser = UBXparser(fid)
    parser.readFile()
