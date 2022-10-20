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
        started = False
        counter = 0
        for i in range(0, len(bin)):

            if not started:
                if bin[i:i+2] == self.pream:
                    started = True
                    counter = 0
                    msglen = int.from_bytes(bin[i+4:i+6] ,byteorder='little', signed=False)+8
                    print(msglen)
                    msg = b''

            if started:
                msg = msg + bin[i:i+1]
                #print(msg)
                #print(counter)
                counter = counter + 1
                    #print(UBXmsg)
                if counter == msglen:
                    started = False
                    try:
                        UBXmsg = UBXmessage(bin=msg)
                    except Exception as err:
                        print(err)





if __name__ == "__main__":
    fid = open("../UBXraw.ubx", 'br')
    parser = UBXparser(fid)
    parser.readFile()
