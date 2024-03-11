import sys
import os
import util
from bitarray import bitarray
from struct import pack, unpack
import logging

#start = bytearray((b'\xB5', b'\x62'))

pream = b'\xB5\x62'
classes = (
    (b'\x01', "NAV",(
        (b'\x22', 'CLOCK'),
        (b'\x04', 'DOP'),
        (b'\x61', 'EOE'),
        (b'\x39', 'GEOFENCE'),
        (b'\x13', 'HPPOSECEF'),
        (b'\x14', 'HPPOSLLH'),#
        (b'\x09', 'ODO'),
        (b'\x34', 'ORB'),
        (b'\x01', 'POSECEF'),
        (b'\x02', 'POSLLH'),
        (b'\x07', 'PVT'),
        (b'\x3C', 'RELPOSNED'),
        (b'\x10', 'RESETODO'),
        (b'\x35', 'SAT'),
        (b'\x43', 'SIG'),
        (b'\x03', 'STATUS'),
        (b'\x3B', 'SVIN'),
        (b'\x24', 'TIMEBDS'),
        (b'\x25', 'TIMEGAL'),
        (b'\x23', 'TIMEGLO'),
        (b'\x20', 'TIMEGPS'),
        (b'\x26', 'TIMELS'),
        (b'\x21', 'TIMEUTC'),
        (b'\x11', 'VELECEF'),
        (b'\x12', 'VELNED')
    )),
    (b'\x02', "RXM", (
        (b'\x14', 'MEASX'),
        (b'\x41', 'PMREQ'),
        (b'\x15', 'RAWX'),
        (b'\x59', 'RLM'),
        (b'\x32', 'RTCM'),
        (b'\x13', 'SFRBX')
    )),
    (b'\x03', "TRK", (
        (b'\x10', 'MEAS'),
    )),
    (b'\x04', "INF", (

    )),
    (b'\x05', "ACK", (

    )),
    (b'\x06', "CFG", (
        (b'\x13', 'ANT'),
        (b'\x09', 'CFG'),
        (b'\x06', 'DAT'),
        (b'\x70', 'DGNSS'),
        (b'\x69', 'GEOFENCE'),
        (b'\x3e', 'GNSS'),
        (b'\x02', 'INF'),
        (b'\x39', 'ITFM'),
        (b'\x47', 'LOGFILTER'),
        (b'\x01', 'MSG'),
        (b'\x24', 'NAV5'),
        (b'\x23', 'NAVX5'),
        (b'\x17', 'NMEA'),
        (b'\x1e', 'ODO'),
        (b'\x00', 'PRT'),
        (b'\x57', 'PWR'),
        (b'\x08', 'RATE'),
        (b'\x34', 'RINV'),
        (b'\x04', 'RST'),
        (b'\x16', 'SBAS'),
        (b'\x71', 'TMODE3'),
        (b'\x31', 'TP5'),
        (b'\x1b', 'USB'),
        (b'\x8c', 'VALDEL'),
        (b'\x8b', 'VALGET'),
        (b'\x8a', 'VALSET')
    )),
    (b'\x09', 'UPD', (

    )),
    (b'\x0A', "MON", (

    )),
    (b'\x0B', "AID", (

    )),
    (b'\x0D', "TIM", (

    )),
    (b'\x13', "MGA", (

    )),
    (b'\x21', "LOG", (

    )),
    (b'\x27', "SEC", (
        (b'\x03', 'UNIQID'),
        (b'\x00', 'MEAS'),
    )),
    (b'\xCA', "CUS", (
        (b'\x01', 'ID'),
    ))
)

class MessageType(Exception):pass


class UBXmessage(object):
    pream = b'\xB5\x62'

    def __new__(cls, **kwargs):
        bin = False
        for k, val in kwargs.items():
            if k == "bin":
                bin = True

        if bin:
            if kwargs['bin'][0:2] == cls.pream:
                return cls._preprocess(cls, **kwargs)
            else:
                raise Exception("Preambulum error!")
        else:
            pass

    def _preprocess(self, **kwargs):

        for c in classes:
            if c[0] == kwargs['bin'][2:3]:
                for i in c[2]:
                    if i[0] == kwargs['bin'][3:4]:
                        return eval("UBX_" + c[1]  + "_" + i[1] + "(**kwargs)")
        raise MessageType("Message type not found!", util.bytesToHexStr(kwargs['bin']))

    def checkClass(self, classId):

        for cl in classes:
            if classId == cl[0]:
                return True
        return False

    def checkMessage(self, classId, messageId):

        for cl in classes:
            if classId == cl[0]:
                for msg in cl[2]:
                    if messageId == msg[0]:
                        return True
        return False

class UBX(object):
    pream = b'\xB5\x62'

    def __init__(self, **kwargs):
        self.data = {}
        #print("XXXXXXXXXXXXXXXXXXX")
        #print(self.data)
        bin = False
        for k, val in kwargs.items():
            if k == "bin":
                bin = True

        if bin:
            self.bin = kwargs['bin']
            if self.bin[0:2] == self.pream:
                self.classid = self.bin[2:3]
                self.id = self.bin[3:4]
                self.len = self.bytes2uint(self.bin[4:6])
                self.payload = self.bin[6:6+self.len]
                self.cs = self.bin[6+self.len:6+self.len+2]

                if self.cs == util.checksum(self.bin[2:6+self.len]):
                    self.decode(self.payload_struct)
                else:
                    raise Exception("Checksum error!")
            else:
                raise Exception("Preambulum error!")
        else:
            msg_type = str(self).split('_')
            for c in classes:
                if c[1] == msg_type[1]:
                    for i in c[2]:
                        if i[1] == msg_type[2]:
                            self.classid = c[0]
                            self.id = i[0]

    def getEpoch(self):
        return (self.data.get('iTOW', 0) *10**(-3)) + (self.data.get('fTOW', 0) *10**(-9))

    def setData(self, **kwargs):
        for e in self.payload_struct_UART:
            if e[1] == 'R':
                continue
            if e[1] == 'X':
                self.data[e[0]] = {}
                for s in e[3]:
                    if s[1] == 'R':
                        continue
                    try:
                        self.data[e[0]][s[0]] = kwargs[s[0]]
                    except KeyError as err:
                        if not s[0] in self.data[e[0]]:
                            self.data[e[0]][s[0]] = eval("self."+s[0])
            else:
                try:
                    self.data[e[0]] = kwargs[e[0]]
                except KeyError as err:
                    if not e[0] in self.data:
                        self.data[e[0]] = eval("self."+e[0])
    def encode(self, payload_struct):
        
        
        i = None
        j = None
        #print(self.payload[16:48])
        #print(self.payload[48:80])
        binary = b''

        for e in payload_struct:
            #print(e)

            if e[0] == "reserved":
                #print(e[2])


                for n in range(e[2]):
                    binary += b'\x00'
                #domain_shift = domain_shift + e[2]
            elif e[0] == "repeat":


                i = 0
                j = 0
                name = e[2]
                ##print(self.data)
                num = self.data[e[1]]
                self.data[name] = []

                self.data[e[2]] = []
                
                
                while num > 0:
                    data = {}
                    for sub in e[3]:
                        if sub[0] != "reserved":
                            data[sub[0]] = self.parseData(self.payload[domain_shift:domain_shift+sub[2]], sub)
                        domain_shift = domain_shift + sub[2]
                    num = num - 1
                    self.data[e[2]].append(data)
            else:
                binary += self.dumpData(self.data[e[0]], e)


        return pream + self.classid + self.id + self.uint2bytes(len(binary), 2) + binary + util.checksum(self.classid + self.id + self.uint2bytes(len(binary), 2) + binary)

    def decode(self, payload_struct):
        domain_shift = 0
        i = None
        j = None
        #print(self.payload[16:48])
        #print(self.payload[48:80])

        for e in payload_struct:
            #print(e)

            if e[0] == "reserved":
                #print(e[2])
                domain_shift = domain_shift + e[2]
            elif e[0] == "repeat":


                i = 0
                j = 0
                name = e[2]
                ##print(self.data)
                num = self.data[e[1]]
                self.data[name] = []

                self.data[e[2]] = []
                
                
                while num > 0:
                    data = {}
                    for sub in e[3]:
                        #
                        #print(self.len)
                        if sub[0] != "reserved":
                            data[sub[0]] = self.parseData(self.payload[domain_shift:domain_shift+sub[2]], sub)
                        domain_shift = domain_shift + sub[2]
                    num = num - 1
                    self.data[e[2]].append(data)
            else:
                #print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx")
                #print(self.parseData(self.payload[domain_shift:domain_shift+e[2]], e))
                self.data[e[0]] = self.parseData(self.payload[domain_shift:domain_shift+e[2]], e)
                domain_shift = domain_shift + e[2]
        


    def parseData(self, bin, msg_struct):
        if msg_struct[1] == "U":#process bytes as unsigned integer
            return self.bytes2uint(bin, msg_struct[3])
        elif msg_struct[1] == "S":#process bytes as signed integer
            return self.bytes2sint(bin, msg_struct[3])
        elif msg_struct[1] == "F":#process bytes as float
            return self.bytes2float(bin, msg_struct[3])
        elif msg_struct[1] == "D":#process bytes as double
            return self.bytes2double(bin, msg_struct[3])
        elif msg_struct[1] == "X":#process bytes as bitfield
            return self.bytes2bitfield(bin, msg_struct[3])
        elif msg_struct[1] == "CH":#process bytes as bitfield
            return bin.decode('ascii')
        else:
            #print(bin)
            raise TypeError("Unknown type: " + msg_struct[1])
        
    def dumpData(self, data, msg_struct):
        if msg_struct[1] == "U":#process bytes as unsigned integer
            return self.uint2bytes(data, msg_struct[2])
        elif msg_struct[1] == "S":#process bytes as signed integer
            return self.sint2bytes(data, msg_struct[2])
        elif msg_struct[1] == "F":#process bytes as float
            return self.float2bytes(data, msg_struct[2])
        elif msg_struct[1] == "D":#process bytes as double
            return self.double2bytes(data, msg_struct[2])
        elif msg_struct[1] == "X":#process bytes as bitfield
            return self.bitfield2bytes(data, msg_struct[3])
        elif msg_struct[1] == "CH":#process bytes as bitfield
            return data.encode('ascii')
        else:
            #print(bin)
            raise TypeError("Unknown type: " + msg_struct[1])

    def bytes2uint(self, bin, scale=1):

        return int.from_bytes(bin ,byteorder='little', signed=False)*scale
    
    def uint2bytes(self, uint, l):
        return uint.to_bytes(l, byteorder='little', signed=False)

    def bytes2sint(self, bin, scale=1):

        return int.from_bytes(bin ,byteorder='little', signed=True)*scale
    
    def sint2bytes(self, sint, l):
        return sint.to_bytes(l, byteorder='little', signed=True)

    def bytes2float(self, bin, scale=1):
        return unpack('f', bin)[0]*scale
    
    def float2bytes(self, fl):
        return pack('f', fl)

    def bytes2double(self, bin, scale=1):
        return unpack('d', bin)[0]*scale
    
    def double2bytes(self, fl):
        return pack('d', fl)

    def bytes2bitfield(self, bin, fields):
        bits = bitarray(endian='little')
        bits.frombytes(bin)

        i = 0
        res = {}
        for f in fields:
            
            if f[1] == 'S':
                res[f[0]] = int.from_bytes(bits[i:i+f[2]].tobytes(), byteorder='big', signed=True)*f[3]
            elif f[1] == 'U':
                res[f[0]] = int.from_bytes(bits[i:i+f[2]].tobytes(), byteorder='big', signed=False)*f[3]
            elif f[1] == 'R':#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                int.from_bytes(bits[i:i+f[2]].tobytes(), byteorder='little', signed=True)
            i = i + f[2]

        return res
    
    def bitfield2bytes(self, data, fields):
        #bits = bitarray(endian='little')
        #bits.frombytes(bin)
        ret_bits = bitarray(endian='little')
        i = 0
        for f in fields:
            
            if f[1] == 'S':
                byte = data[f[0]].to_bytes(int(f[2]/8)+1, byteorder='big', signed=True)
                bits = bitarray(endian="little")
                bits.frombytes(byte)
                bits = bits[0:f[2]]
            elif f[1] == 'U':
                byte = data[f[0]].to_bytes(int(f[2]/8)+1, byteorder='big', signed=False)
                bits = bitarray(endian="little")
                bits.frombytes(byte)
                bits = bits[0:f[2]]
            elif f[1] == 'R':
                bits = bitarray()
                for i in range(f[2]):
                    bits += '0'
            
            ret_bits += bits
            
            i = i + f[2]

        return ret_bits.tobytes()
        
    
    def __str__(self):
        return type(self).__qualname__
    
    def pollMsg(self):
        msg_name = str(self).split("_")
        for c in classes:
            if msg_name[1] != c[1]:
                break
            for id in c[2]:
                if id[1] == msg_name[2]:
                    
                    clid = c[0] + id[0]
                    
                    break
            #for id in c:
        b = clid + b'\x00\x00'
        return pream + b + util.checksum(b)


class UBX_UNKNOWN(UBX):
    pass

class UBX_NAV(UBX):

    #class_byte = 0x01

    #struct = ("U1", "U1", "U1", "U1", "U4", "I4", "I4", "I4", "I1e_2", )

    #def __init__(self):
    #    pass
    def _preprocess(self, **kwargs):
        for c in self.IDs:
            if c[0] == self.bin[3:4]:
                return eval("UBX_NAV_" + c[1] + "(**kwargs)")

class UBX_NAV_CLOCK(UBX_NAV):

    payload_struct = [
    ("iTOW", "U", 4, 1),
    ("clkB", "S", 4, 1),
    ("clkD", "S", 4, 1),
    ("tAcc", "U", 4, 1),
    ("fAcc", "U", 4, 1)
    ]
class UBX_NAV_DOP(UBX_NAV):

    payload_struct = [
    ("iTOW", "U", 2, 0.01),
    ("gDOP", "U", 2, 0.01),
    ("pDOP", "U", 2, 0.01),
    ("tDOP", "U", 2, 0.01),
    ("vDOP", "U", 2, 0.01),
    ("hDOP", "U", 2, 0.01),
    ("nDOP", "U", 2, 0.01),
    ("eDOP", "U", 2, 0.01)
    ]

class UBX_NAV_EOE(UBX_NAV):

    payload_struct = [
    ("iTOW", "U", 4, 1)
    ]

class UBX_NAV_GEOFENCE(UBX_NAV):

    payload_struct = [
    ("iTOW", "U", 4, 1),
    ("version", "U", 1, 1),
    ("status", "U", 1, 1),
    ("numFences", "U", 2, 1),
    ("combState", "U", 2, 1),
    ("repeat", "numFences", "fences", 2),
    ("state", "U", 1, 1),
    ("reserved", "R", 1, 1),
    ("stop", )
    ]

class UBX_NAV_HPPOSECEF(UBX_NAV):
    
    payload_struct = [
    ("version", "U", 1, 1),
    ("reserved", "R", 1, 1),
    ("iTOW", "U", 4, 1),
    ("ecefX", "S", 4, 1),
    ("ecefY", "S", 4, 1),
    ("ecefZ", "S", 4, 1),
    ("ecefXHp", "S", 1, 0.1),
    ("ecefYHp", "S", 1, 0.1),
    ("ecefZHp", "S", 1, 0.1),
    ("reserved", "R", 1, 1),
    ("pAcc", "U", 4, 0.1)
    ]

class UBX_NAV_HPPOSLLH(UBX_NAV):

    payload_struct = [
    ("version", "U", 1, 1),
    ("reserved", "R", 2, 1),
    ("flags", "X", 1, (
        ("invalidLlh", "U", 1, 1),
    )),
    ("iTOW", "U", 4, 1),
    ("lon", "S", 4, 10**-7),
    ("lat", "S", 4, 10**-7),
    ("height", "S", 4, 1),
    ("hMSL", "S", 4, 1),
    ("lonHp", "S", 1, 10**-9),
    ("latHp", "S", 1, 10**-9),
    ("heightHp", "S", 1, 0.1),
    ("hMSLHp", "S", 1, 0.1),
    ("hAcc", "U", 4, 0.1),
    ("vAcc", "U", 4, 0.1)
    ]

    @property
    def lat(self):
        return self.data['lat']+self.data['latHp']
    @property
    def lon(self):
        return self.data['lon']+self.data['lonHp']
    @property
    def height(self):
        return (self.data['height']+self.data['heightHp']/1000)/1000
    @property
    def heightMSL(self):
        return (self.data['hMSL']+self.data['hMSLHp']/1000)/1000
    @property
    def hAcc(self):
        return self.data['hAcc']
    @property
    def vAcc(self):
        return self.data['vAcc']

class UBX_NAV_STATUS(UBX_NAV):

    payload_struct = [
    ("iTOW", "U", 4, 1),
    ("gpsFix", "U", 1, 1),
    ("flags", "X", 1, (
        ("gpsFixOk", "U", 1, 1),
        ("diffSoln", "U", 1, 1),
        ("wknSet", "U", 1, 1),
        ("towSet", "U", 1, 1)
    )),
    ("fixStat", "X", 1, (
        ("diffCorr", "U", 1, 1),
        ("carrSolnValid", "U", 1, 1),
        ("reserved", "R", 4, 1),
        ("mapMatching", "U", 2, 1)
    )),
    ("flags2", "X", 1, (
        ("psmState", "U", 2, 1),
        ("reserved", "R", 1, 1),
        ("spoofDetState", "U", 2, 1),
        ("reserved", "R", 1, 1),
        ("carrSoln", "U", 2, 1)
    )),
    ("ttff", "U", 4, 1),
    ("msss", "U", 4, 1)
    ]

class UBX_NAV_TIMEGPS(UBX_NAV):

    payload_struct = [
    ("iTOW", "U", 4, 1),
    ("fTOW", "S", 4, 1),
    ("week", "S", 2, 1),
    ("leapS", "S", 1, 1),
    ("valid", "X", 1, (
        ("towValid", "U", 1, 1),
        ("weekValid", "U", 1, 1),
        ("leapSValid", "U", 1, 1)
    )),
    ("tAcc", "U", 4, 1)
    ]

class UBX_NAV_TIMEUTC(UBX_NAV):

    payload_struct = [
    ("iTOW", "U", 4, 1),
    ("tAcc", "U", 4, 1),
    ("nano", "S", 4, 1),
    ("year", "U", 2, 1),
    ("month", "U", 1, 1),
    ("day", "U", 1, 1),
    ("hour", "U", 1, 1),
    ("min", "U", 1, 1),
    ("sec", "U", 1, 1),
    ("valid", "X", 1, (
        ("validTOW", "U", 1, 1),
        ("validWKN", "U", 1, 1),
        ("validUTC", "U", 1, 1),
        ("reserved", "R", 1, 1),
        ("utcStandard", "U", 5, 1)
    ))
    ]

#class UBX_NAV_POSECEF(UBX_NAV):



    #ID = b'\x13'

    #def __init__(self):
    #    pass


#    def _decode(self):pass


class UBX_NAV_POSLLH(UBX_NAV):

    payload_struct = [
    ("iTOW", "U", 4, 1),
    ("lon", "S", 4, 10**-7),
    ("lat", "S", 4, 10**-7),
    ("height", "S", 4, 1),
    ("hMSL", "S", 4, 1),
    ("hAcc", "U", 4, 1),
    ("vAcc", "U", 4, 1)
    ]

    @property
    def lat(self):
        return self.data['lat']
    @property
    def lon(self):
        return self.data['lon']
    @property
    def height(self):
        return self.data['height']/1000
    @property
    def heightMSL(self):
        return self.data['hMSL']/1000
    @property
    def hAcc(self):
        return self.data['hAcc']
    @property
    def vAcc(self):
        return self.data['vAcc']


class UBX_NAV_SAT(UBX_NAV):

    payload_struct = [
    ("iTOW", "U", 4, 1),
    ("version", "U", 1, 1),
    ("numSvs", "U", 1, 1),
    ("reserved", "R", 2, 1),
    ("repeat", "numSvs", "measurements", (
        ("gnssId", "U", 1, 1),
        ("svId", "U", 1, 1),
        ("cno", "U", 1, 1),
        ("elev", "S", 1, 1),
        ("azim", "S", 2, 1),
        ("prRes", "S", 2, 0.1),
        ("flags", "X", 4, (
            ("qualityInd", "U", 3, 1),
            ("svUsed", "U", 1, 1),
            ("health", "U", 2, 1),
            ("diffCorr", "U", 1, 1),
            ("smoothed", "U", 1, 1),
            ("orbitSource", "U", 3, 1),
            ("ephAvail", "U", 1, 1),
            ("almAvail", "U", 1, 1),
            ("anoAvail", "U", 1, 1),
            ("aopAvail", "U", 1, 1),
            ("sbasCorrUsed", "U", 1, 1),
            ("rtcmCorrUsed", "U", 1, 1),
            ("slasCorrUsed", "U", 1, 1),
            ("spartnCorrUsed", "U", 1, 1),
            ("prCorrUsed", "U", 1, 1),
            ("crCorrUsed", "U", 1, 1),
            ("doCorrUsed", "U", 1, 1),
            ("clasCorrUsed", "U", 1, 1),
        )),
    ))
    ]

    @property
    def measurements(self):
        for data in self.data['measurements']:
            yield data


    def __str__(self):
        return type(self).__qualname__ + " visible sats: " + str(len(self.data['measurements']))


class UBX_NAV_SIG(UBX_NAV):

    payload_struct = [
    ("iTOW", "U", 4, 1),
    ("version", "U", 1, 1),
    ("numSigs", "U", 1, 1),
    ("reserved", "R", 2, 1),
    ("repeat", "numSigs", "measurements", (
        ("gnssId", "U", 1, 1),
        ("svId", "U", 1, 1),
        ("sigId", "U", 1, 1),
        ("freqId", "U", 1, 1),
        ("prRes", "S", 2, 1),
        ("cno", "U", 1, 1),
        ("qualityInd", "U", 1, 1),
        ("corrSource", "U", 1, 1),
        ("ionoModel", "U", 1, 1),
        ("sigFlags", "X", 2, (
            ("health", "U", 2, 1),
            ("prSmoothed", "U", 1, 1),
            ("prUsed", "U", 1, 1),
            ("crUsed", "U", 1, 1),
            ("doUsed", "U", 1, 1),
            ("prCorrUsed", "U", 1, 1),
            ("crCorrUsed", "U", 1, 1),
            ("doCorrUsed", "U", 1, 1),
        )),
        ("reserved", "R", 4, 1),
    ))
    ]
    
    @property
    def measurements(self):
        for data in self.data['measurements']:
            yield data
            

#class UBX_NAV_HPPOSLLH(UBX_NAV):
#    pass

class UBX_RXM(UBX):

    #class_byte = 0x01

    #struct = ("U1", "U1", "U1", "U1", "U4", "I4", "I4", "I4", "I1e_2", )

    #def __init__(self):
    #    pass
    def _preprocess(self, **kwargs):
        for c in self.IDs:
            if c[0] == self.bin[3:4]:

                return eval("UBX_RXM_" + c[1] + "(**kwargs)")

class UBX_RXM_RAWX(UBX_RXM):

    payload_struct = [
    ("rcvTow", "D", 8, 1),
    ("week", "U", 2, 1),
    ("leapS", "S", 1, 1),
    ("numMeas", "U", 1, 1),
    ("recStat", "X", 1, (
        ("leapSec", "U", 1, 1),
        ("clkReset", "U", 1, 1),
        ("reserved", "R", 6, 1)
    )),
    ("version", "U", 1, 1),
    ("reserved", "R", 2, 1),
    ("repeat", "numMeas", "measurements", (
        ("prMes", "D", 8, 1),
        ("cpMes", "D", 8, 1),
        ("doMes", "F", 4, 1),
        ("gnssId", "U", 1, 1),
        ("svId", "U", 1, 1),
        ("sigId", "U", 1, 1),
        ("freqId", "U", 1, 1),
        ("locktime", "U", 2, 1),
        ("cno", "U", 1, 1),
        ("prStdev", "X", 1, (
            ("prStd", "U", 4, 0.01*2**1),#?????????????????????????????????????????has to be clearified
            ("reserved", "R", 4, 1)
        )),
        ("cpStdev", "X", 1, (
            ("cpStd", "U", 4, 0.004),
            ("reserved", "R", 4, 1)
        )),
        ("doStdev", "X", 1, (
            ("doStd", "U", 4, 0.002*2**1),#?????????????????????????????????????????has to be clearified
            ("reserved", "R", 4, 1)
        )),
        ("trkStat", "X", 1, (
            ("prValid", "U", 1, 1),
            ("cpValid", "U", 1, 1),
            ("halfCyc", "U", 1, 1),
            ("subhalfCyc", "U", 1, 1),
            ("reserved", "R", 4, 1)
        )),
        ("reserved", "R", 1, 1)
    ))
    ]
    @property
    def measurements(self):
        for data in self.data['measurements']:
            yield data

    def getEpoch(self):
        return self.data['rcvTow']

class UBX_RXM_RTCM(UBX_RXM):

    payload_struct = [
    ("version", "U", 1, 1),
    ("flags", "X", 1, (
        ("crcFailed", "U", 1, 1),
        ("msgUsed", "U", 2, 1)
    )),
    ("subType", "U", 2, 1),
    ("refStation", "U", 2, 1),
    ("msgType", "U", 2, 1)
    ]

class UBX_CFG(UBX):

    #class_byte = 0x01

    #struct = ("U1", "U1", "U1", "U1", "U4", "I4", "I4", "I4", "I1e_2", )

    #def __init__(self):
    #    pass
    def _preprocess(self, **kwargs):
        for c in self.IDs:
            if c[0] == self.bin[3:4]:

                return eval("UBX_CFG_" + c[1] + "(**kwargs)")


class UBX_CFG_GETVAL(UBX_RXM):
    payload_struct = [
    ("version", "U", 1, 1),
    ("layer", "U", 1, 1),
    ("postion", "U", 2, 1),
    ("repeat", "numMeas", "keys", (
        ("keys", "U", 4, 1),
    ))
    ]

class UBX_CFG_PRT(UBX_CFG):
    #Default UART settings
    en=0
    pol=0
    pin=0
    thres=0
    charLen=3
    parity=4
    nStopBits=0
    baudRate=9600
    inUbx=1
    inNmea=1
    inRtcm=0
    inRtcm3=1
    outUbx=1
    outNmea=1
    outRtcm3=1
    extendedTxTimeout=0

    payload_struct = [
        ("portID", "U", 1, 1),
        ("reserved", "R", 19, 1)
    ]
    
    payload_struct_UART = [
        ("portID", "U", 1, 1),
        ("reserved", "R", 1, 1),
        ("txReady", "X", 2, (
            ("en", "U", 1, 1),
            ("pol", "U", 1, 1),
            ("pin", "U", 5, 1),
            ("thres", "U", 9, 1)
        )),
        ("mode", "X", 4, (
            ("reserved", "R", 6, 1),
            ("charLen", "U", 2, 1),
            ("reserved", "R", 1, 1),
            ("parity", "U", 3, 1),
            ("nStopBits", "U", 2, 1),
            ("reserved", "R", 18, 1)
        )),
        ("baudRate", "U", 4, 1),
        ("inProtoMask", "X", 2, (
            ("inUbx", "U", 1, 1),
            ("inNmea", "U", 1, 1),
            ("inRtcm", "U", 1, 1),
            ("reserved", "R", 2, 1),
            ("inRtcm3", "U", 1, 1),
            ("reserved", "R", 10, 1)
        )),
        ("outProtoMask", "X", 2, (
            ("outUbx", "U", 1, 1),
            ("outNmea", "U", 1, 1),
            ("reserved", "R", 3, 1),
            ("outRtcm3", "U", 1, 1),
            ("reserved", "R", 10, 1)
        )),
        ("flags", "X", 2, (
            ("reserved", "R", 1, 1),
            ("extendedTxTimeout", "U", 1, 1),
            ("reserved", "R", 14, 1)
        )),
        ("reserved", "R", 2, 1)
    ]

    def decode(self, payload_struct):
        super().decode(payload_struct)
        
        if self.data['portID'] == 0:#i2c
            pass
        elif self.data['portID'] == 1 or self.data['portID'] == 2:#UART
            super().decode(self.payload_struct_UART)
        elif self.data['portID'] == 3:#USB
            pass
        elif self.data['portID'] == 4:#SPI
            pass

    def encode(self):

        if self.data['portID'] == 0:#i2c
            pass
        elif self.data['portID'] == 1 or self.data['portID'] == 2:#UART
            return super().encode(self.payload_struct_UART)
        elif self.data['portID'] == 3:#USB
            pass
        elif self.data['portID'] == 4:#SPI
            pass
class UBX_SEC(UBX):

    #class_byte = 0x01

    #struct = ("U1", "U1", "U1", "U1", "U4", "I4", "I4", "I4", "I1e_2", )

    #def __init__(self):
    #    pass
    def _preprocess(self, **kwargs):
        for c in self.IDs:
            if c[0] == self.bin[3:4]:

                return eval("UBX_SEC_" + c[1] + "(**kwargs)")

class UBX_SEC_UNIQID(UBX_SEC):
    

    payload_struct = [
    ("version", "U", 1, 1),
    ("reserved", "R", 1, 1),
    ("reserved", "R", 1, 1),
    ("reserved", "R", 1, 1),
    ("uniqueId1", "U", 1, 1),
    ("uniqueId2", "U", 1, 1),
    ("uniqueId3", "U", 1, 1),
    ("uniqueId4", "U", 1, 1),
    ("uniqueId5", "U", 1, 1)
    ]


class UBX_TRK_MEAS(UBX_SEC):
    '''
    UBX-TRK-MEAS message
    '''
    

    payload_struct = [
    ("unk1", "U", 2, 1),
    ("nch", "U", 2, 1),
    ("unk2", "U", 100, 1),
    ("repeat", "nch", "measurements", (
        ("chn", "U", 1, 1),
        ("unk1", "U", 1, 1),
        ("mesQI", "U", 1, 1),
        ("unk2", "U", 1, 1),
        ("system", "U", 1, 1),
        ("svid", "U", 1, 1),
        ("unk3", "U", 1, 1),
        ("fcn", "U", 1, 1),
        ("status", "U", 1, 1),
        ("unk4", "U", 7, 1),
        ("lock1", "U", 1, 1),
        ("lock2", "U", 1, 1),
        ("unk5", "U", 2, 1),
        ("cno", "U", 2, 2**-8),
        ("unk6", "U", 2, 1),
        ("txTow", "S", 8, 2**-32),
        ("adr", "S", 8, 2**-32),
        ("dop", "S", 4, 2**-32*10),
        ("unk7", "U", 12, 1),
    ))
    ]

class UBX_CUS(UBX):

    #class_byte = 0x01

    #struct = ("U1", "U1", "U1", "U1", "U4", "I4", "I4", "I4", "I1e_2", )

    #def __init__(self):
    #    pass
    def _preprocess(self, **kwargs):
        for c in self.IDs:
            if c[0] == self.bin[3:4]:

                return eval("UBX_CUS_" + c[1] + "(**kwargs)")

class UBX_CUS_ID(UBX_CUS):

    payload_struct = [
    ("ID", "CH", 4, 1),
    ]


if __name__ == "__main__":

    #aaa = b'\xb5b\x02\x15\x10\x06\x98n\x12\x03\xd0\x87\x12A\xc7\x08\x120\x01\x01\xe1\x0c\t\x0e\x1a\xac\xb5\xa0\x82A\xf3\x00\xb6Y\xefx\xa8A\xf0O\x0b\xc3\x01{\x00\x00\xf4\xfb.\x03\x01\x06\x0f\x00Kn\xf6\x89\xd9\xa4\x82A1\x1d,\xc6_~\xa8A\x80e\x08\xc3\x01\x88\x00\x00\xf4\xfb-\x03\x01\x06\x0f\x00\x84\x0c\xa4P\xea}uA]}\x0c\x141<\x9cA\xa8L\n\xc5\x00\x13\x00\x00\xf4\xfb \x06\x05\x08\x0f\x00\x89\x8e\x1d\xe9m\x14|A\xce\x96\x1b\x13\xeeq\xa2A)M#\xc5\x02\x01\x00\x00\xf4\xfb-\x03\x01\x05\x07\x00W1\xd1\xe5>=xAE)\n\xd9\x16\x8e\x9fAX6FE\x03\x1c\x00\x00\xf4\xfb-\x03\x01\x06\x0f\x00AN&\x08w?\x83A\xb1\xcb\x0be\xa6\x0e\xa9A\x1c\xa9_\xc4\x03\n\x00\x00\xf4\xfb)\x04\x02\x07\x07\x00\xe5\x9f\xaa\xc4m%wA\x1d\xa8\xef\xb3\xd1!\x9eA\x16\x9c\x85\xc4\x03\x0b\x00\x00\xf4\xfb+\x03\x02\x06\x07\x00\xca\xcc\\\xb1O\xc1\x83A\xfb.\x98l\xaf\xb7\xa9Al\x82\x85\xc4\x03\x07\x00\x00\xf4\xfb&\x04\x02\x07\x0f\x00\xf0\x87\xbeJ\x8f\xb9xA\xec\xe7\xfb(\x04\x02\x07\x07\x00D\xd1<\xb7v,xAw\xf2\x11\xfc<x\x9fA\xa7g\x0c\xc5\x03"\x00\x00\xf4\xfb\x1b\x06\x07\x08\x07\x00\x03\x02ow\xa2\xe3uA=\xd2\x8a\xff\xe5~\x9cA4\x9b\x86\xc4\x03\x17\x00\x00\xf4\xfb2\x03\x01\x05\x0f\x00\xaa\x80bt\xcd\xb5vA26>\xf5\x9fN\x9eA\xfb\x1b\x8aE\x06\x12\x00\x04\xf4\xfb-\x05\x01\x06\x0f\x00\xbfT\x95\x8bg\x10vA\x9a\xe7\xf5\x10Kg\x9dA\x86\x99C\xc5\x06\x0e\x00\x00\xf4\xfb3\x05\x01\x04\x07\x00\xc4\xbaqOq"wA\xf0k\xa6 \xd3\xf5\x9eA\xe6\n\x1bE\x06\x07\x00\x0c\x00\x00\x15\n\x0f\x0c\x01\x00\xd7\xca\xc0ZO&tA\x9e\xda\x96\x83\xcc\xf4\x9aA\x123\x03E\x06\x11\x00\x0b\xf4\xfb2\x05\x01\x04\x07\x00Kh\xd9\xc0\n2tAj.\xb2^/\x88\x9aAJ\x06\xb2\xc4\x00\x18\x00\x00\xf4\xfb1\x03\x01\x05\x07\x00\x9f}?wa\x10zA\xfd>\x8c\x06\xf2\x1e\xa1As\xcfA\xc5\x02\t\x00\x00\xf4\xfb(\x05\x02\x07\x07\x00\xbb\x8a\x10\xfd\xee\xd3vA \xf4[a\x86\xfd\x9dA<S\xcaD\x00\x06\x00\x00\xf4\xfb+\x03\x02\x06\x07\x00\xf9T\xadz\xe0\xdewA:\xba\x1a(8\\\x9fAc6\xb6\xc4\x02\x1f\x00\x00\xf4\xfb.\x03\x01\x05\x07\x00\x1fw.L\x83\xffzA\x0fm\xb3\x12\x08\xbc\xa1A\xa1\xd88E\x02\x0c\x00\x00\xf4\xfb%\x05\x02\x07\x07\x00\xb7\x18$U,\xa5yA\xce\x92\xa7\x17\x88\xd8\xa0A\x805\xa7D\x02!\x00\x00\xf4\xfb0\x03\x01\x05\x07\x00\xaea/\xe0=\xb2|AP\xb9Xj\x98\xd9\xa2A-\xa5rE\x02\x0e\x00\x00\xf4\xfb#\x05\x03\x07\x07\x00\xc9\xbc\xa5*\x88"xA\xd0\x14\x8c!\x1a\xb5\x9fA\x0c\xd3;E\x00\x0b\x00\x00\xf4\xfb+\x03\x01\x06\x0f\x00\r\xa4\x92@\x83\xffzA\x11\x8c\xefxt-\x9bA\x9d\x9f\rE\x02\x0c\x06\x00\xf4\xfb%\x04\x03\x07\x07\x00\x9b\xceh\nm%wA\xea\xa9\x8d@\xd0L\x97A\xd0\xb2N\xc4\x03\x0b\x02\x00\xf4\xfb/\x03\x01\x05\x0f\x00wyDOO\xc1\x83A\xcfIIZ\xeb\xe2\xa3A|\x84N\xc4\x03\x07\x02\x00\xf4\xfb)\x03\x02\x07\x0f\x00\xfe\r\x83\xc0v?\x83A5\x9a\x88x6`\xa3A\xf8\xfa,\xc4\x03\n\x02\x00\xf4\xfb)\x03\x02\x06\x07\x00\x90\x87}\r>\xb2|A\xfd*\x90\xb1\x11\xe3\x9cAL\xf29E\x02\x0e\x06\x00\xf4\xfb\'\x03\x02\x06\x07\x00\xa8\xfd\xach\xe0\xdewA\xe9\xb3w\xca}\x07\x98A\x16\xa0\x8b\xc4\x02\x1f\x06\x00\xf4\xfb+\x03\x01\x06\x07\x00y\xc4w\x18n\x14|A\xbaRv\xdc3D\x9cA\xc4@\xfa\xc4\x02\x01\x06\x00\xf4\xfb.\x03\x01\x05\x07\x00\x9d\xf1\xd3\x7fx\xafzA\xa5Pq\xe7\xdf\xdc\x9aA<\xc8V\xc4\x02\x1a\x06\x00\xf4\xfb\x1d\x06\x07\t\x07\x00\xe0Y\x04Da\x10zAE)\xafu\xb9<\x9aA\x91\x81\x14\xc5\x02\t\x06\x00\xf4\xfb+\x03\x01\x06\x07\x00\xb8\xc0\x99\x04#7{A\x9d\x83\x85uqe\x9bAW\xfc\xd7D\x02\x19\x06\x00\x00\x00\x1a\x08\x0f\n\x01\x00\xb1i\xd7G,\xa5yA\xe1)\x9b\x9c\xd0\xd0\x99A\xd8\x1b\x80D\x02!\x06\x00\xf4\xfb2\x03\x01\x04\x07\x00\xea\x1aIO\n2tA|\x85\x89\x14\x9c\xac\x94A\x8c\xb6\x8a\xc4\x00\x18\x03\x00\xf4\xfb*\x04\x02\x06\x07\x00\xc8\'\xa4\xfb\xdc\xc6xA\xd6L5\xa9>]\x99AG\xd3<\xc5\x00\x0f\x03\x00\xf4\xfb\x1f\x06\x06\x08\x0f\x00iL9#\x82-uA\x8f\xd8T\xbf/\x05\x96A\xb2:\xca\xc4\x06\x18\x02\t\xbcM\x1c\x07\x07\x08\x0f\x00/\xbd~\xcc\x87"xA\xa6\tK\xd9\x03\xb5\x98AHW\x12E\x00\x0b\x03\x00\xf4\xfb$\x05\x03\x08\x07\x00\x02\x89\xac\xf8\xee\xd3vAy\x9d\xec\x81}^\x97A\xe2\xa2\x9dD\x00\x06\x03\x00\xf4\xfb.\x04\x01\x06\x07\x00O/\xe9\x9eg\x10vA\xa9\\\\\x1c\x8e\xde\x96A\x1e!\x18\xc5\x06\x0e\x02\x00\xf4\xfb/\x05\x01\x05\x07\x00\xb2\xe1\xde\x98\xcd\xb5vA\xfc\xe5v\x05{\x92\x97A}\xd6VE\x06\x12\x02\x04\xf4\xfb\'\x05\x02\x07\x07\x00\xa8\n%\xf3N&tA\xde|\x08\x13I\xf7\x94A\x00\x12\xccD\x06\x11\x02\x0b\xf4\xfb,\x05\x01\x06\x0f\x00\x05B\xb5b\x02\x150\x06\x98n\x12\x03\xd4\x87\x12A\xc7\x08\x121\x01\x01\xc9\x10\x82%Q\x7f\xb6\xa0\x82A\xef\xee\x91p\xf0x\xa8A\xe0\xb1\x0b\xc3\x01{\x00\x00\xf4\xfb.\x03\x01\x06\x0f\x00\xee\xf1\xc8Y\xda\xa4\x82A\xba3\xf0\xd6`~\xa8A \x95\x08\xc3\x01\x88\x00\x00\xf4\xfb-\x03\x01\x06\x0f\x00\xdaR0\xa1\x04~uAdV|\xaaS<\x9cA\xf9b\n\xc5\x00\x13\x00\x00\xf4\xfb \x06\x05\x08\x0f\x00z\x00f\xfd\x8c\x14|A\xa8H\xc9|\x02r\xa2A\xf4P#\xc5\x02\x01\x00\x00\xf4\xfb-\x03\x01\x05\x07\x00\xd6\x81\xaa\xd7\x18=xAn\x0f\xf0K\xe5\x8d\x9fA\'1FE\x03\x1c\x00\x00\xf4\xfb-\x03\x01\x06\x0f\x00_f\x8eg|?\x83A\xf8<fb\xad\x0e\xa9A\x88\xbf_\xc4\x03\n\x00\x00\xf4'
    #aaa = b'\xb5b\x01\x14$\x00\x00\x00\x00\x00`\x9e0\x08]\r\\\x0b\xaf\x81L\x1c\xd61\x02\x00/\x98\x01\x00\xe4\x0c\x01\x01\xb9\xb0\x04\x00$x\xb5b\x02\x15'
    #aaa = b'\xb5b\x02\x15\x90\x01\xd1"\xdb\xf9_o\x02A\xcb\x08\x12\x0c\x01\x01 N\xc6\xe7=\xc2\x16\x99tA\xff\x11ZW\x91\x0f\x9bA\xae1,E\x00\x08\x00\x00\xf4\xfb,\x04\x01\x06\x07\x00\xc8\xd0u|\xd9{rA\x1cN\x85`\x82H\x98A\xe8\xc2\x8bD\x00\x1b\x00\x00\xf4\xfb/\x03\x01\x06\x0f\x00\x0eR\xd3Ep5uAd\xab\xab\xc0 \x9c\x9bA\xaa9\xfcD\x03\x0c\x00\x00\xf4\xfb)\x03\x02\x06\x0f\x003\xa13(\x94\x8csA\xfd\xeb.\xf3M\r\x9aA\xcc1\x18D\x06\x0e\x00\x00\xf4\xfb-\x05\x02\x06\x07\x00\x0b\xd4\xaat\xdd\xc9qA\x93\xf9B\xe9\x06\xca\x97A\x81d\xf7C\x06\x17\x00\n\xf4\xfb(\x05\x02\x07\x07\x00=\x87V\xe6w3tALR\t\xf1\x8a\x01\x9bA\xbb\xd70E\x06\x18\x00\t\xf4\xfb(\x05\x02\x07\x07\x00\xbe\xa7\x1f\xado5uA\x93e\xf4\xb8\x85Y\x95A\x0c\x07\xc3D\x03\x0c\x02\x00\xf4\xfb&\x04\x03\x07\x07\x00\x04\xeeg\xb6\x16\x99tA/\x0e\xd6\xf5\x1a\x16\x95A\xcd.\x06E\x00\x08\x03\x00\xf4\xfb\x1f\x06\x06\t\x07\x00\n\xe0AO\xd9{rAsK\x11\n\x0f\x0c\x01\x005\x90\x90\xdaw3tA\xeawh\xef2\x01\x95Az\x9a\tE\x06\x18\x02\t\xf4\xfb\x1f\x07\x06\t\x0f\x00"\x1eN\x8e\xe7FvA\xb6\x824|\x9d%\x97A`}0E\x06\x0f\x02\x07\x00\x00\x13\x0b\x0f\x0c\x01\x00\xc8\xb5\xb5b\x01\x14$\x00\x00\x00\x00\x00\xe0a\x00\t:}[\x0be8M\x1c0\xb4\x02\x00\x83\x1a\x02\x00\xf0\xd9\x00\x00W\xac\x04\x00\xa8\x8e\x04\x005\r\xb5b\x01\x03'
    #aaa = b"\xb5b\x03\x10\x8c\x06\x02\x00\x1b\x03\x00\x00\x00\x001\xa0\x03\x00\xd0\x9f\x03\x00\xe8\x03\x7f\x01,\xe9\xd3\xa7\xff\xff\xff\xff\xed\xff\xff\xff\xff\xff\xff\xff0\x08c\x00\x00\x00\x00\x80\x07\xe8\xd3\xa7c\xce\xee\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00O\x00\x00\x00O\x00\x00\x00\x00\x00\x00\x00O\x00\x00\x00O\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x10\x00\x06\x00\x00\x00\x03\x00\x02\x02*(\x8a#Q\x00\x08\xa9\x00\x00\x03\xa6\x0e\xe8\x00\x92_\xdd\xf9\x8cm\x83\x94Z}{\x12f\x00\x00o\xcc\x01\x00\x89\xedG\x00\x903\x0b\x00\xff_+C\x01\x06\x00\x00\x00\x00\x10\xaa?<\x86#1g\x08\xfb\xfb\xfb\x00\xc1\x1c\xe8\x00\xe6:\xb6\x82\x85m\x83\xe3\xbf=\xae\xd2\x9d\x01\x00\xcb\x98\x00\x00_\xdf\x17\x00%g\x01\x00\x03\x06\x03\x04\x02\x03\x00\x00\x00\x04\x00\x03\x00*\x08\x01\x00\x00\x08\x00\x00\x00\x00\x00\x00\xff\xff\xb0\xcd1\x85\x89m\x83\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\xd8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x06\x00\x00\x00\x00\x12\xaa?<\x86#1g\x08\xfb\xfb\xfb\x00\x86\x1e\xe8\x00\xaf\xb1B\\\x85m\x83@o\t&%9\x07\x00\xeb\xfd\x02\x00k\xadw\x00\t\x02\x01\x00\x02\x06\x03\x04\x04\x03\x00\x00\x00\x02\x00\x01\x00*\x08\x01\x00\x00\x08\x00\x00\x00\x00\x00\x00\xff\xff\x18'\x12\n\x85m\x83\xecQ\x98\xc1\xf7\xff\xff\xff\x00\x00\x00\x00\x00\xa0\x95\xff\x00\x00\x00\x00\x00\x00\x00\x00\x05\x03\x00\x00\x00\x1f\x00\x1e\x00*\x08\x01\x00\x00\x08\x00\x00\x00\x00\x00\x00\xff\xffp\xa0\xbaE\x86m\x83\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 |\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x03\x00\x00\x00\x15\x00\x14\x00*\x08\x01\x00\x00\x08\x00\x00\x00\x00\x00\x00\xff\xff\x18\x0f\x19v\x82m\x83\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd0\x8c\xff\x00\x00\x00\x00\x00\x00\x00\x00\x07\x03\x00\x00\x00\x1c\x00\x1b\x00*\x08\x01\x00\x00\x08\x00\x00\x00\x00\x00\x00\xff\xff\xc0\xd8\x99\xa4\x83m\x83\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00@\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x03\x00\x00\x01|\x00\x04\x00\x00\x08\x01\x00\x00\x08\x00\x00\x00\x00\x00\x00\xff\xff\xa0Y\xc0\x90Qm\x83\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00`E\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\x06\x00\xf7\x06\x17\x00\n*?<\x86#1g\n\xfb__\x00\x8e\x19\xe8\x08\xea\xcafr\xbf\xf2'\x12KEu\xd1\x99,\x05\x00\x120\x02\x00\rxW\x00\xd9\xcf\x01\x06\x05\x08\x04\x05\n\x06\x00\xfc\x06\x08\x00\r\x02+(\x8a#Q\x01\n\xfb\x00\x00\x00\xdf\x16\xe8\x08\xd4\x81\xfc\xbe\xf2'\x12]\x8f\x8f~v\xfb\x06\x00\xf9>\x03\x00\xfcv\x81\x00\x06\xc1\x0b\x01\xff_+C\x0b\x04\x00\xf9\x06\x07\x00\x0c\x00*\x08\x01\x00\x00\n\x00\x00\x00\x00\x00\x00\xff\xff\xe0(\xa9\xf7\xbc\xf2'\x12{\x14\xb0\xc2\xf0\xff\xff\xff\x00\x00\x00\x00\x00\xa0\xb4\xff\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x04\x00\x01\x06\x16\x00\x04\x00*\x08\x01\x00\x00\n\x00\x00\x00\x00\x00\x00\xff\xff\x00\xf2\xd0\r\xba\xf2'\x12\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00P^\xff\x00\x00\x00\x00\x00\x00\x00\x00\r\x05\x00\xfd\x06\x18\x00\t\x02?(\xaa#Q\x07\n\xfb\x00\x00\x05\xa1\x0f\xe8\x08\xa0\x9b\x91\xe8\xb5\xf2'\x12\xb3n\xa3?\xcd\x80\x0e\x00b\xa8\x07\x00-\x892\x01\x9dW\x15\x08\xff\xbdU\x85\x0e\x04\x00\x02\x06\x10\x00\x06\x00*\x08\x01\x12\x00\x00\n\x00\x00\x00\x00\x00\x00\xff\xff\xba\x08\x00P\xb3\xf2'\x12\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00PO\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\x04\x00\xfc\x06\x01\x00\x08\x00*\x08\x01\x00\x00\n\x00\x00\x00\x00\x00\x00\xff\xff\xe0\xed`F\xb3\xf2'\x12\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa0 \x01\x00\x00\x00\x00\x00\x00\x00\x00\x10\x04\x00\x03\x06\t\x00\x05\x00*\x08\x01\x00\x00\n\x00\x00\x00\x00\x00\x00\xff\xffp\x02v5\xb2\xf2'\x12\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00p\x02\x01\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x01~\x00\x06\x00\x00\x08\x01\x00\x00\x08\x00\x00\x00\x00\x00\x00\xff\xff\xf8'\xf8:Qm\x83\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00PE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x12\x03\x00\x00\x00\t\x00\x08\x00*\x08\x01\x00\x00\x08\x00\x00\x00\x00\x00\x00\xff\xffH\x8d\xa6V\x82m\x83\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00P\x1d\x01\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x01x\x00\x00\x00\x00\x08\x01\x00\x00\x08\x00\x00\x00\x00\x00\x00\xff\xff\xc0':\x02Nm\x83\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00`E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x14\x04\x00\x00\x06\x0f\x00\x07\x00*\x08\x01\x00\x00\n\x00\x00\x00\x00\x00\x00\xff\xff0SN\xd8\xad\xf2'\x12\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00p\x9f\xff\x00\x00\x00\x00\x00\x00\x00\x00\x15\x03\x00\x00\x00 \x00\x1f\x00*\x08\x01\x00\x00\x08\x00\x00\x00\x00\x00\x00\xff\xffP\x01vWzm\x83\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 m\xff\x00\x00\x00\x00\x00\x00\x00\x00\x16\x03\x00\x00\x00\x06\x00\x05\x00*\x08\x01\x00\x00\x08\x00\x00\x00\x00\x00\x00\xff\xff\xf8p\xea\xc8~m\x83\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00P!\x01\x00\x00\x00\x00\x00\x00\x00\x00\x17\x04\x00\x00\x06\x06\x00\x03\x00*\x08\x01\x00\x00\n\x00\x00\x00\x00\x00\x00\xff\xff\x80\x04K\xc8\xaf\xf2'\x12\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0[\xff\x00\x00\x00\x00\x00\x00\x00\x00\x18\x02\x00\x00\x05\x05\x00\x04\x00\x00\x08\x01\x00\x00\x08\x00\x00\x00\x00\x00\x00\xff\xff@\xda\xd6\x01Tm\x83\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x90n\xff\x00\x00\x00\x00\x00\x00\x00\x00\x19\x02\x00\x00\x05\x01\x00\x00\x00\x00\x08\x01\x00\x00\x08\x00\x00\x00\x00\x00\x00\xff\xff\xc8\x0c\xf3\xe8Sm\x83\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x000{\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1a\x02\x00\x00\x05\x02\x00\x01\x00\x00\x08\x01\x00\x00\x08\x00\x00\x00\x00\x00\x00\xff\xff\xc8\x0c\xf3\xe8Sm\x83\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x000{\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\r\x00\x00\x00\x00\x00\x1a\x00\xab \x00\x00\x10\x08@\x7f\x00\x00\x12\r\x00\x00\x00\x00\x00x\x00\x0c\x17\x00\x00\x10\x08@!\x00\x1c\x00\x1b-\x00\x00\x00\x00p\x07\x00\x90)\x00\x00\r\x08$NA\xf1\xb5b\x03\x10x\x06\x02\x00\x1b\x02\x00\x00\x00\x00\x19\xa4\x03\x00\xb8\xa3\x03\x00\xe8\x03\x7f\x01,U\xb0\xaa\xff\xff\xff\xff\xed\xff\xff\xff\xff\xff\xff\xff0\x08"
    #aaa = b'\xb5b\x02\x15\x90\x00D\x8bl\xe7_\xf1\xfa@\xc8\x08\x12\x04\x01\x01>\xf5\xd1\xcb\x8e\x0e,\xefrARlh\xe9\x03\xe0\x98A\x15\n\x06\xc5\x00\x07\x00\x00\x00\x00\x13\t\x0f\x0c\x01\x00u\x03\x8c\xba\xf1\x94uA\x030#\xc8qZ\x9cA\x00[PD\x00\x08\x00\x00\x00\x00\x0c\n\x0f\r\x01\x00\x0fc\x0b4i\x90tA\x13*.qbv\x9bA[\xf4\x87\xc5\x06\x10\x00\x06\x00\x00\x13\n\x0f\r\x01\x00\xd3q\x99\t\xdf\xa1uA\x1bQElmk\x9cAS\xa00\xc4\x02\x19\x00\x00\x00\x00\x10\t\x0f\x0c\x01\x00V\xb8'
    #msg = UBXmessage(bin=aaa)
    #print(msg.data)

    aaa = b'\xb5\x62\06\x00\x14\x00\x01\x00\x00\x00\xD0\x08\x00\x00\x80\x25\x00\x00\x23\x00\x23\x00\x00\x00\x00\x00\xde\x55' 
    msg = UBXmessage(bin=aaa)
    #print(msg.data)
    #msg.setData(outNmea=0, outRtcm3=1)
    print(util.bytesToHexStr(msg.encode()))
    #msg = UBX_CFG_PRT()
    #print(msg.sint2bytes(-1, 1))
    #print(msg.data)
