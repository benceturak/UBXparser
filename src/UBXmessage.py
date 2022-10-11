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
        (b'\x14', 'HPPOSLLH'),
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
    (b'\x02', "RXM"),
    (b'\x04', "INF"),
    (b'\x05', "ACK"),
    (b'\x06', "CFG"),
    (b'\x09', 'UPD'),
    (b'\x0A', "MON"),
    (b'\x0B', "AID"),
    (b'\x0D', "TIM"),
    (b'\x13', "MGA"),
    (b'\x21', "LOG"),
    (b'\x27', "SEC")
    )

    def __new__(cls, **kwargs):
        bin = False
        print(kwargs)
        for k, val in kwargs.items():
            if k == "bin":
                bin = True

        if bin:
            cls.bin = kwargs['bin']
            if cls.bin[0:2] == cls.pream:
                return cls._preprocess(cls, **kwargs)
            else:
                raise Exception()
        else:
            pass

    def _preprocess(self, **kwargs):

        for c in self.classes:
            if c[0] == self.bin[2:3]:
                print(c[2])
                for i in c[2]:
                    print(i[0])
                    if i[0] == self.bin[3:4]:
                        return eval("UBX_" + c[1]  + "_" + i[1] + "(**kwargs)")

class UBX(object):

    def __init__(self, **kwargs):
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
        pass
    def decode(self):
        pass

    def unsigned_int(self, bin, scale=1):

        return int.from_bytes(bin ,byteorder='little', signed=False)*scale

    def signed_int(self, bin, scale=1):

        return int.from_bytes(bin ,byteorder='little', signed=True)*scale

    def bitfield(self, bin, fields):
        bits = bitarray(endian='little')
        bits.frombytes(bin)

        i = 0
        res = []
        for f in fields:
            print(f[0])
            if f[1] == 'S':
                signed = True
            elif f[1] == 'U':
                signed = False
            res.append(int.from_bytes(bits[i:i+f[0]].tobytes(), byteorder='big', signed=signed))
            i = i + f[0]

        return res

class UBX_NAV(UBX):

    class_byte = 0x01

    struct = ("U1", "U1", "U1", "U1", "U4", "I4", "I4", "I4", "I1e_2", )

    #def __init__(self):
    #    pass
    def _preprocess(self, **kwargs):
        for c in self.IDs:
            if c[0] == self.bin[3:4]:

                return eval("UBX_NAV_" + c[1] + "(**kwargs)")

class UBX_NAV_POSECEF(UBX_NAV):


    ID = b'\x13'

    #def __init__(self):
    #    pass

    def _preprocess(self, **kwargs):
        pass#for

    def _decode(self):
        pass

msg = UBXmessage(bin=b'\xB5\x62\x01\x01\x09')

print(msg)

#print(msg.bitfield(b'\xd7', ((2, 'U'),(2, 'U'),(2, 'U'),(2, 'U'))))

print(msg._checksum(b'\x12\xab\x12\x01\x13\xab\x12\xab\x12\xab\x12\xab\x12\xab\x12\xab\x12\xab\x12\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab'))






#
