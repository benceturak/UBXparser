from bitarray import bitarray

#start = bytearray((b'\xB5', b'\x62'))


class UBXmessage(object):
    pream = b'\xB5\x62'

    classes = (
    (b'\x01', "NAV"),
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

    def __init__(self, msg):
        if msg[0:2] == self.pream:
            self.msg = msg
        else:
            raise Exception()



        for c in self.classes:
            print(c[0])
            if c[0:1] == msg[1:2]:
                aaa = UBX_NAV

    def _checksum(self):
        pass

    def _parse(self):
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
            res.append(int.from_bytes(bits[i:i+f].tobytes(), byteorder='big'))
            i = i + f

        return res









class UBX_NAV(UBXmessage):

    class_byte = 0x01
    IDs = (
    ('\x22', 'CLOCK'),
    ('\x04', 'DOP'),
    ('\x61', 'EOE'),
    ('\x39', 'GEOFENCE'),
    ('\x13', 'HPPOSECEF'),
    ('\x14', 'HPPOSLLH'),
    ('\x09', 'ODO'),
    ('\x34', 'ORB'),
    ('\x01', 'POSECEF'),
    ('\x02', 'POSLLH'),
    ('\x07', 'PVT'),
    ('\x3C', 'RELPOSNED'),
    ('\x10', 'RESETODO'),
    ('\x35', 'SET'),
    ('\x43', 'SIG'),
    ('\x03', 'STATUS'),
    ('\x3B', 'SVIN'),
    ('\x24', 'TIMEBDS'),
    ('\x25', 'TIMEGAL'),
    ('\x23', 'TIMEGLO'),
    ('\x20', 'TIMEGPS'),
    ('\x26', 'TIMELS'),
    ('\x21', 'TIMEUTC'),
    ('\x11', 'VELECEF'),
    ('\x12', 'VELNED')
    )

    struct = ("U1", "U1", "U1", "U1", "U4", "I4", "I4", "I4", "I1e_2", )

    def __init__(self):
        pass

class UBX_NAV_POSECEF(UBX_NAV):

    ID = b'\x13'

    def __init__(self):
        pass

    def _parse(self):
        pass

msg = UBXmessage(b'\xB5\x62\x01\x01\x09')

print(msg.bitfield(b'\xd7', ((2, 'U'),(2, 'U'),(2, 'U'),(2, 'U')))






#
