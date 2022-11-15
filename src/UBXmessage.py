from bitarray import bitarray
from struct import pack, unpack

#start = bytearray((b'\xB5', b'\x62'))


class UBXmessage(object):
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
        (b'\x35', 'SET'),
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
    )

    ),
    (b'\x02', "RXM", (
        (b'\x14', 'MEASX'),
        (b'\x41', 'PMREQ'),
        (b'\x15', 'RAWX'),
        (b'\x59', 'RLM'),
        (b'\x32', 'RTCM'),
        (b'\x13', 'SFRBX')
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
    ))
    )

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

        for c in self.classes:
            if c[0] == kwargs['bin'][2:3]:
                for i in c[2]:
                    if i[0] == kwargs['bin'][3:4]:
                        try:
                            return eval("UBX_" + c[1]  + "_" + i[1] + "(**kwargs)")
                        except NameError as er:
                            print(er)


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
                #print("CHECKSUM")
                #print(self._checksum(self.bin[2:6+self.len]))
                #print(self.cs)
                if self.cs == self._checksum(self.bin[2:6+self.len]):
                    self.decode()
                else:
                    raise Exception("Checksum error!")
            else:
                raise Exception("Preambulum error!")
        else:
            pass

    def _checksum(self, msg):
        cs_a = 0
        cs_b = 0

        for b in msg:
            cs_a = cs_a + b
            cs_b = cs_b + cs_a

        cs_a = cs_a%256
        cs_b = cs_b%256

        cs_a = cs_a.to_bytes(1, 'big')
        cs_b = cs_b.to_bytes(1, 'big')

        return cs_a + cs_b

    def encode(self):
        print()
    def decode(self):
        domain_shift = 0
        i = None
        j = None
        #print(self.payload[16:48])
        #print(self.payload[48:80])

        for e in self.payload_struct:
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
            return self.bitfield(bin, msg_struct[3])
        else:
            print(bin)
            raise TypeError("Unknown type " + bin[1] + "!")

    def bytes2uint(self, bin, scale=1):

        return int.from_bytes(bin ,byteorder='little', signed=False)*scale

    def bytes2sint(self, bin, scale=1):

        return int.from_bytes(bin ,byteorder='little', signed=True)*scale

    def bytes2float(self, bin, scale=1):
        return unpack('f', bin)[0]*scale

    def bytes2double(self, bin, scale=1):
        return unpack('d', bin)[0]*scale

    def bitfield(self, bin, fields):
        bits = bitarray(endian='little')
        bits.frombytes(bin)

        i = 0
        res = {}
        for f in fields:
            
            if f[1] == 'S':
                signed = True
                res[f[0]] = int.from_bytes(bits[i:i+f[2]].tobytes(), byteorder='big', signed=True)*f[3]
            elif f[1] == 'U':
                signed = False
                res[f[0]] = int.from_bytes(bits[i:i+f[2]].tobytes(), byteorder='big', signed=False)*f[3]
            elif f[1] == 'R':
                int.from_bytes(bits[i:i+f[2]].tobytes(), byteorder='little', signed=True)
            i = i + f[2]

        return res

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
    ("reserved", "U", 1, 1),
    ("stop", )
    ]

class UBX_NAV_HPPOSECEF(UBX_NAV):

    payload_struct = [
    ("version", "U", 1, 1),
    ("reserved", "U", 1, 1),
    ("iTOW", "U", 4, 1),
    ("ecefX", "S", 4, 1),
    ("ecefY", "S", 4, 1),
    ("ecefZ", "S", 4, 1),
    ("ecefXHp", "S", 1, 0.1),
    ("ecefYHp", "S", 1, 0.1),
    ("ecefZHp", "S", 1, 0.1),
    ("reserved", "U", 1, 1),
    ("pAcc", "U", 4, 0.1)
    ]

class UBX_NAV_HPPOSLLH(UBX_NAV):

    payload_struct = [
    ("version", "U", 1, 1),
    ("reserved", "U", 1, 1),
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
    ("hz_acc", "U", 4, 1),
    ("v_acc", "U", 4, 1)
    ]



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
















#
