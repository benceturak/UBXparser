import _io
import queue
from UBXmessage import UBXmessage
import serial



class UBXparser(object):

    pream = b'\xB5\x62'

    def __init__(self, source):
        if isinstance(source, _io.BufferedReader):
            self.source = source
            self.sourceType = "file"
        elif isinstance(source, queue.Queue):
            self.source = source
            self.sourceType = "queue"
            self.stopQueue = False
        else:
            raise TypeError("Invalid source type!")
    def readQueue(self):
        if self.sourceType != "queue":
            raise TypeError("Invalid source type! Type must be queue!")

        bin = b''
        counter = 0
        while True:
            if self.source.empty():
                continue
            bin += self.source.get()

            msg = b''
            started = False
            

            counter = counter + 1
            binLen = len(bin)
            print("BINLEN")
            print(binLen)
            for i in range(0, binLen):
                print('A')
                print(i)

                if bin[i:i+2] == self.pream:
                    print("START")
                    started = True
                    counter = 0
                    msglen = int.from_bytes(bin[i+4:i+6] ,byteorder='little', signed=False)+8
                    #print(msglen)
                    startIndex = i
                    endIndex = i + msglen

                    print(endIndex)
                    print(binLen)

                    if binLen >= endIndex:
                        msg = bin[startIndex:endIndex] 
                        bin = bin[endIndex:]
                        print("STARTINDEX")
                        print(startIndex)
                        try:
                            UBXmsg = UBXmessage(bin=msg)
                        except Exception as err:
                            print(msg)
                            print(UBXmsg._checksum(msg[2:msgLen-2]))
                            print(self.cs)
                            print(err)

                    else:

                        print("BREAK")
                        break


                    

    def readFile(self):
        if self.sourceType != "file":
            raise TypeError("Invalid source type! Type must be file!")
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
                    #print(msglen)
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
    #fid = open("../UBXraw.ubx", 'br')
    ser = serial.Serial("/dev/ttyACM0", 115200)

    import _thread

    q = queue.Queue()

    def read_ser(ser):
        while True:
            q.put(ser.read_until())

    _thread.start_new_thread(read_ser, (ser,))



    #while True:
    #    print('AAA')
    #    print(q.get())

    parser = UBXparser(q)
    parser.readQueue()
