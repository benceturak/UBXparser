from bitarray import bitarray

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
                raise Exception()
        else:
            pass

    def _preprocess(self, **kwargs):

        for c in self.classes:
            if c[0] == kwargs['bin'][2:3]:
                for i in c[2]:
                    if i[0] == kwargs['bin'][3:4]:
                        try:
                            a = eval("UBX_" + c[1]  + "_" + i[1] + "(**kwargs)")
                            print(a.bin)
                        except NameError as er:
                            print(er)


class UBX(object):
    pream = b'\xB5\x62'

    def __init__(self, **kwargs):
        self.data = {}
        print("XXXXXXXXXXXXXXXXXXX")
        print(self.data)
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

                if self.cs == self._checksum(self.bin[2:6+self.len]):
                    self.decode()
                else:
                    raise Exception()
            else:
                raise Exception()
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
        for e in self.payload_struct:
            if e[0] == "reserved":
                continue
            elif e[0] == "repeat":
                i = 0
                j = 0
                name = e[2]
                print("aaaaaaa")
                print(self.data)
                num = self.data[e[1]]
                self.data[name] = []

                print(num)
                for k in range(0,num):
                    self.data[name].append({})
                    print(k)
                print(self.data)

                tags = e[3]
                continue
            elif e[0] == "stop":
                continue

            if e[1] == "U":#process bytes as unsigned integer
                value = self.bytes2uint(self.payload[domain_shift:domain_shift+e[2]], e[3])
            elif e[1] == "S":#process bytes as signed integer
                value = self.bytes2sint(self.payload[domain_shift:domain_shift+e[2]], e[3])
            elif e[1] == "F":#process bytes as float
                value = self.bytes2float(self.payload[domain_shift:domain_shift+e[2]], e[3])
            elif e[1] == "D":#process bytes as double
                value = self.bytes2double(self.payload[domain_shift:domain_shift+e[2]], e[3])
            elif e[1] == "X":#process bytes as bitfield
                value = self.bitfield(self.payload[domain_shift:domain_shift+e[2]], e[3])
            else:
                raise TypeError("Unknown type " + e[1] + "!")
            if i == None:
                self.data[e[0]] = value
            else:
                if i == num:
                    continue
                self.data[name][i] = value
                j = j + 1
                if j == tags:
                    i = i + 1
                    j = 0




            domain_shift = domain_shift + e[2]
        #self.iTOW = self.bytes2uint(self.payload[0:4])

        print(self.data)

    def bytes2uint(self, bin, scale=1):

        return int.from_bytes(bin ,byteorder='little', signed=False)*scale

    def bytes2sint(self, bin, scale=1):

        return int.from_bytes(bin ,byteorder='little', signed=True)*scale

    def bytes2float(self, bin, scale=1):
        return float.from_bytes(bin ,byteorder='little', signed=True)*scale

    def bytes2double(self, bin, scale=1):
        return double.from_bytes(bin ,byteorder='little', signed=True)*scale

    def bitfield(self, bin, fields):
        bits = bitarray(endian='little')
        bits.frombytes(bin)

        i = 0
        res = {}
        for f in fields:
            print(f[0])
            if f[1] == 'S':
                signed = True
            elif f[1] == 'U':
                signed = False
            res[b[0]] = int.from_bytes(bits[i:i+f[2]].tobytes(), byteorder='big', signed=signed)
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

                return eval("UBX_NAV_" + c[1] + "(**kwargs)")

class UBX_RXM_RAWX(UBX_RXM):

    payload_struct = [
    ("rcvTow", "D", 8, 1),
    ("week", "U", 2, 1),
    ("leapS", "S", 1, 1),
    ("numMeas", "U", 1, 1),
    ("recStat", "X", 1, (
        ("leapSec", "U", 1),
        ("clkReset", "U", 1),
        ("reserved", "U", 6)
    )),
    ("version", "U", 1, 1),
    ("reserved", "U", 1, 1),
    ("repeat", "numMeas", "measurements", 14),
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
        ("prStd", "U", 4),
        ("reserved", "U", 4)
    )),
    ("doStdev", "X", 1, (
        ("cpStd", "U", 4),
        ("reserved", "U", 4)
    )),
    ("trkStat", "X", 1, (
        ("prValid", "U", 1),
        ("cpValid", "U", 1),
        ("halfCyc", "U", 1),
        ("subhalfCyc", "U", 1),
        ("reserved", "U", 4)
    )),
    ("reserved", "U", 1, 1),
    ("stop,")
    ]






















#
