import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(sys.path[0])), 'mobile_GNSS'))
import util
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
        elif isinstance(source, (list, tuple)):
            self.source = source
            self.sourceType = "list"

        else:
            raise TypeError("Invalid source type!")
    
    def readQueue(self, shutFunc=lambda: False):
        if self.sourceType != "queue":
            raise TypeError("Invalid source type! Type must be queue!")

        bin = b''
        msgId = 0
        
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
                        util.bytesToHexStr(cs),
                        util.bytesToHexStr(util.checksum(msg[2:6+msgLen])),
                        msgLen,
                        len(msg)
                        ))
                    lastMsgEnd = endIndex
                    continue

                logging.debug("MSG OK, determining type...")
                
                try:
                    
                    ubxMsg = UBXmessage.UBXmessage(bin=msg)
                    logging.info("[{}]: {}".format(round(ubxMsg.getEpoch()), str(ubxMsg)))
                    lastMsgEnd = endIndex
                    yield ubxMsg
                except UBXmessage.MessageType as err:
                    logging.error("MsgType error ({}) while parsing:".format(err, util.bytesToHexStr(msg)))
                except Exception as err:
                    logging.error("Error ({}) while parsing:".format(err, util.bytesToHexStr(msg)))
                            
            bin = bin[lastMsgEnd:]

        logging.info("Parser queue reader stopped")

    def readFile(self):
        if self.sourceType == "file":
            bin = self.source.read()
        elif self.sourceType == "list":
            bin = b''
            for src in  self.source:
                bin += src.read()
        else:
            raise TypeError("Invalid source type! Type must be file!")
        

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
                except UBXmessage.MessageType as err:
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
    def addRAWX(self, a):
        pass

    def readRAWX(self, gnss=None, sat=None, sig=None, mesType=None, removeDuplicated=True):
        """
            :param gnss: GNSS system identifier
            :param sat: satellite identifier
            :param sig: signal identifier
            :param type: observation type [pseudo range, phase, cno, doppler]
        """

        import consts
        import numpy as np

        if self.sourceType == 'file' or self.sourceType == 'list':
            gen = self.readFile()
        elif self.sourceType == 'queue':
            gen = self.readQueue()
        else:
            return 0
        
        res = {}


        sigList = {}
        for gId, system in consts.gnssID.items():
            "gnss system filter"
            if gnss == None:
                pass
            else:
                if system not in gnss:
                    continue
                
            for sId, sigName in consts.sigID[gId].items():

                try:
                    sigList[gId][sId] = sigName
                except KeyError:
                    sigList[gId] = {sId: sigName}

        for msg in gen:
            if not isinstance(msg, UBXmessage.UBX_RXM_RAWX):
                continue

            
            
            for ms in msg.data['measurements']:
                #print(consts.gnssID[ms['gnssId'][0]])
                if not consts.gnssID[ms['gnssId']][0] in gnss:
                    continue

                PRN = consts.gnssID[ms['gnssId']][0]+"{:02d}".format(ms['svId'])

                row = np.array([[ms['prMes'], ms['cpMes'], ms['doMes'], ms['freqId'], ms['locktime'], ms['cno'], ms['prStdev']['prStd'], ms['cpStdev']['cpStd'], ms['doStdev']['doStd'], ms['trkStat']['prValid'], ms['trkStat']['cpValid'], ms['trkStat']['halfCyc'], ms['trkStat']['subhalfCyc']]])
                
                row = np.append([[msg.data["week"], msg.data["rcvTow"]]], row, axis=1)
                #if ms['gnssId'] == 0 and PRN == "G23":
                    #print(row)
                #print(consts.sigID[ms['gnssId']][ms['sigId']])
                    #print(res)
                freq = consts.sigID[ms['gnssId']][ms['sigId']][0]
                try:
                    res[PRN][freq] = np.append(res[PRN][freq], row, axis=0)
                except KeyError as err:
                    try:
                        res[PRN][freq] = row
                    except KeyError:
                        res[PRN] = {freq: row}

        #remove duplicated
        if not removeDuplicated:
            return res
        #print(res)
        for sat in res.keys():
            for sig in res[sat].keys():
                res[sat][sig] = np.unique(res[sat][sig], axis=0)
                #res[sat][sig] = list(set(res[sat][sig]))
        return res







if __name__ == "__main__":
    import numpy as np
    #fid = open("/home/bence/Downloads/COM4_200405_020642/COM4_200405_020642.ubx", 'br')
    #fid = open("/home/pi/refr_test/COM5___38400_230527_114251.ubx", 'br')
    fid = open("/home/bence/talaj/talaj/ubx/down/SAT02_2024-10-08-18.ubx", 'br')
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

    #ser = serial.Serial("/dev/ttyACM0", 115200)

    #import _thread

    #q = queue.Queue()

    #def read_ser(ser):
    #    while True:
    #        q.put(ser.read(10))

    #_thread.start_new_thread(read_ser, (ser,))

    #parser = UBXparser(q)

    #for msg in parser.readQueue():
    #    print(msg.bin)
    
    #exit()
    parser = UBXparser(fid)
    for msg in parser.readFile():
        print('___________________________________')

        #print(msg.data)
        try:
            if isinstance(msg, UBXmessage.UBX_NAV_HPPOSLLH):
                print(msg.lat*np.pi/180, msg.lon*np.pi/180, msg.height)
            if isinstance(msg, UBXmessage.UBX_NAV_SIG):
                print(msg.data['numSigs'])
        except Exception as err:
            print(err)
        #print(msg.data)
        #print(type(msg))
        #for i in msg.measurements:
        #    print(i)
