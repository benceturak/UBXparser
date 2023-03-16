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

    def _checksum(self, msg):
        cs_a = 0
        cs_b = 0

        for b in msg:
            cs_a = (cs_a + b)%256
            cs_b = (cs_b + cs_a)%256

        return ((cs_b << 8) | cs_a).to_bytes(2,'little')

    
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
                logging.info(len(bin))
                logging.info("bin+")
            except queue.Empty as err:
                pass
                #print("Queue error!")
                #logging.warning("Queue timeout! Queue is empty!")
             #logging.info("GET FROM QUEUE")

            binLen = len(bin) 
            lastMsgEnd = 0 
            
            if binLen < 6:
                continue
            for i in range(0, binLen):
                if bin[i:i+2] != self.pream:
                    continue
                msglen = int.from_bytes(bin[i+4:i+6], byteorder='little', signed=False)
                startIndex = i
                endIndex = i + msglen + 8

                
                if len(bin) < endIndex:
                    logging.info("Message length error!")
                    logging.info(msglen)
                    logging.warning(startIndex)
                    logging.info(bin[startIndex:endIndex] )
                    continue
                msg = bin[startIndex:endIndex]  
                

                cs = msg[6+msglen:6+msglen+2]

                if cs != self._checksum(msg[2:6+msglen]):
                    logging.warning("_______________________")
                    logging.warning(startIndex)
                    logging.warning(msg)
                    logging.warning(msg[2:6+msglen])
                    logging.warning("Checksum")
                    logging.warning(self._checksum(msg[2:6+msglen]))
                    logging.warning(cs)
                    logging.warning(len(msg))

                    continue
                logging.info("OK")
                
                try:
                    
                    ubxMsg = UBXmessage.UBXmessage(bin=msg)
                    logging.info("Msg received:"+str(ubxMsg))
                    try:
                        logging.info(ubxMsg.getEpoch())
                    except:
                        pass
                    if isinstance(ubxMsg, UBXmessage.UBX_NAV_EOE):
                        print(ubxMsg.data)
                    lastMsgEnd = endIndex
                    logging.info(lastMsgEnd)
                    yield ubxMsg
                except UBXmessage.MessageType:
                    logging.error(err)
                    logging.info(msg)
                except Exception as err:
                    logging.warning(err)
                    logging.info(msg)
                    print(err)
                    
                            
            logging.info(lastMsgEnd)
            
            bin = bin[lastMsgEnd:]
            logging.info(bin)
            logging.info("Bin reload------------------------------------------------------------")
        print("ReadQueue stops!")

    def readFile(self):
        if self.sourceType != "file":
            raise TypeError("Invalid source type! Type must be file!")
        bin = self.source.read()

        msg = b''   
        binLen = len(bin)





        for i in range(0, binLen):

            if bin[i:i+2] == self.pream:
                msglen = int.from_bytes(bin[i+4:i+6], byteorder='little', signed=False)
                startIndex = i
                endIndex = i + msglen + 8

                if len(bin) < endIndex:
                    logging.info("Message length error!")
                    logging.info(msglen)
                    logging.info(bin[startIndex:endIndex] )
                    continue
                msg = bin[startIndex:endIndex]  
                lastMsgEnd = endIndex

                cs = msg[6+msglen:6+msglen+2]

                if cs != self._checksum(msg[2:6+msglen]):
                    logging.warning("_______________________")
                    logging.warning(msg)
                    logging.warning(msg[2:6+msglen])
                    logging.warning("Checksum")
                    logging.warning(self._checksum(msg[2:6+msglen]))
                    logging.warning(cs)
                    logging.warning(len(msg))

                    continue
                logging.info("OK")
                try:
                    
                    ubxMsg = UBXmessage.UBXmessage(bin=msg)
                    logging.info("Msg received:"+str(ubxMsg))
                    lastMsgEnd = endIndex
                    print(type(ubxMsg))
                    if isinstance(ubxMsg, UBXmessage.UBX_NAV_EOE):
                        print(ubxMsg.data)
                    yield ubxMsg
                except UBXmessage.MessageType:
                    logging.error(err)
                    logging.info(msg)
                except Exception as err:
                    logging.warning(err)
                    logging.info(msg)
                    print(err)

                #else:
                #    print("msg length")
                #    logging.info("Message length error!")
                #    logging.info(bin)
                    #break
        #bin = bin[endIndex:]
        """
        for i in range(0, binLen):

            if bin[i:i+2] == self.pream:
                msglen = int.from_bytes(bin[i+4:i+6], byteorder='little', signed=False)+8
                startIndex = i
                endIndex = i + msglen


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







if __name__ == "__main__":
    fid = open("/home/bence/data/nmea_server/TES1/TES1_22496_23.UBX", 'br')
    
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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

    parser = UBXparser(fid)
    for msg in parser.readFile():

        if isinstance(msg, UBXmessage.UBX_NAV_STATUS):
            print(msg.data)
        #try:
        #    if isinstance(msg, UBXmessage.UBX_NAV_HPPOSLLH):
        #        print(msg.data)
        #except Exception as err:
        #    print(err)
        #print(msg.data)
        #print(type(msg))
        #for i in msg.measurements:
        #    print(i)
