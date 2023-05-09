import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(sys.path[0])), 'mobile_GNSS'))
from common import util
import _io
import queue

import UBXmessage
import serial
import logging


class MessageLength(Exception):pass


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
    
    def readQueue(self, shutFunc=lambda: False):
        if self.sourceType != "queue":
            raise TypeError("Invalid source type! Type must be queue!")

        bin = b''
        
        while True:
            if shutFunc():
                logging.info("Stop read queue")
                break
            try:
                bin += self.source.get(block=True, timeout=1)
                logging.debug("Read {} bytes".format(len(bin)))
            except queue.Empty as err:
                continue

            binLen = len(bin) 
            lastMsgEnd = 0 
            
            if binLen < 6:
                continue
            for i in range(0, binLen):
                if bin[i:i+2] != self.pream:
                    continue
                msgLen = int.from_bytes(bin[i+4:i+6], byteorder='little', signed=False)
                startIndex = i
                endIndex = i + msgLen + 8

                if len(bin) < endIndex:
                    continue

                msg = bin[startIndex:endIndex]
                cs = msg[6+msgLen:6+msgLen+2]

                if cs != util.checksum(msg[2:6+msgLen]):
                    logging.warning("Invalid checksum: {} instead of {} in msg of length {}/{}".format(
                        util.bytesToHexStr(msg[msgLen-2:msgLen]),
                        util.bytesToHexStr(util.checksum(msg[2:6+msgLen])),
                        msgLen,
                        len(msg)
                        ))
                    continue

                logging.debug("MSG OK, determining type...")
                
                try:
                    
                    ubxMsg = UBXmessage.UBXmessage(bin=msg)
                    logging.info("Msg received: {} at {}".format(str(ubxMsg), ubxMsg.getEpoch()))
                    lastMsgEnd = endIndex
                    yield ubxMsg
                except UBXmessage.MessageType as err:
                    logging.error("MsgType error ({}) while parsing:".format(err, util.bytesToHexStr(msg)))
                except Exception as err:
                    logging.error("Error ({}) while parsing:".format(err, util.bytesToHexStr(msg)))
                            
            bin = bin[lastMsgEnd:]

        logging.info("Parser queue reader stopped")

    def readFile(self):
        if self.sourceType != "file":
            raise TypeError("Invalid source type! Type must be file!")
        bin = self.source.read()

        msg = b''   
        binLen = len(bin)
        print("Parsing binary file (size: {}B)".format(binLen))
        lastLoggedStep = 0
        logEveryNthPercent = 10
        logEveryNthByte = binLen / logEveryNthPercent

        for i in range(0, binLen):

            if i > logEveryNthByte * (lastLoggedStep + 1):
                lastLoggedStep += 1
                print("{}%".format(lastLoggedStep * logEveryNthPercent))

            if bin[i:i+2] == self.pream:
                msgLen = int.from_bytes(bin[i+4:i+6], byteorder='little', signed=False)
                startIndex = i
                endIndex = i + msgLen + 8

                if len(bin) < endIndex:
                    logging.info("Message length error!")
                    logging.info(msgLen)
                    logging.info(bin[startIndex:endIndex] )
                    continue
                msg = bin[startIndex:endIndex]  
                lastMsgEnd = endIndex

                cs = msg[6+msgLen:6+msgLen+2]

                if cs != util.checksum(msg[2:6+msgLen]):
                    '''
                    logging.warning("_______________________")
                    logging.warning(msg)
                    logging.warning(msg[2:6+msgLen])
                    logging.warning("Checksum")
                    logging.warning(util.checksum(msg[2:6+msgLen]))
                    logging.warning(cs)
                    logging.warning(len(msg))
                    '''
                    continue
                logging.info("OK")
                try:
                    
                    ubxMsg = UBXmessage.UBXmessage(bin=msg)
                    logging.info("Msg received:"+str(ubxMsg))
                    lastMsgEnd = endIndex
                    #print(type(ubxMsg))
                    #if isinstance(ubxMsg, UBXmessage.UBX_NAV_EOE):
                        #print(ubxMsg.data)
                    yield ubxMsg
                except UBXmessage.MessageType:
                    logging.error(err)
                    logging.info(msg)
                except Exception as err:
                    logging.warning(err)
                    logging.info(msg)
                    #print(err)

                #else:
                #    print("msg length")
                #    logging.info("Message length error!")
                #    logging.info(bin)
                    #break
        #bin = bin[endIndex:]
        """
        for i in range(0, binLen):

            if bin[i:i+2] == self.pream:
                msgLen = int.from_bytes(bin[i+4:i+6], byteorder='little', signed=False)+8
                startIndex = i
                endIndex = i + msgLen


                if len(bin) >= endIndex:
                    msg = bin[startIndex:endIndex] 
                    
                    
                    try:
                        ubxMsg = UBXmessage.UBXmessage(bin=msg)
                        yield ubxMsg
                    
                    
                    except Exception as err:
                        logging.warning(err)
                        logging.info(msg)
                        print(err)
                                
                    continue

                else:
                    logging.warning("Message length error!")
                    logging.info(bin)
                    raise MessageLength("Message length error!")
        """

#if __name__ == "__main__":
    #fid = open("d:/BME/_ur/2/proj/UBX_sample/TES1_22532_11.UBX", 'br')
    
    #logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    #ser = serial.Serial("/dev/ttyACM0", 115200)

    #import _thread

    #q = queue.Queue()

    #def read_ser(ser):
    #    while True:
    #        q.put(ser.read(10))

    #_thread.start_new_thread(read_ser, (ser,))



    #while True:
    #    print('AAA')
    #    print(q.get())

    #parser = UBXparser(fid)
    #for msg in parser.readFile():

        #if isinstance(msg, UBXmessage.UBX_NAV_STATUS):
            #print(msg.data)
        #try:
        #    if isinstance(msg, UBXmessage.UBX_NAV_HPPOSLLH):
        #        print(msg.data)
        #except Exception as err:
        #    print(err)
        #print(msg.data)
        #print(type(msg))
        #for i in msg.measurements:
        #    print(i)
