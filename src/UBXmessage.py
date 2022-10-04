

start = 0xB562

class UBXmessage(object):





    def __init__(self, msg):
        pass

    def _checksum(self):
        pass

    def _parse(self):
        pass

class UBX_NAV(UBXmessage):

    class_bit = 0x01

    def __init__(self):
        pass

class UBX_NAV_POSECEF(UBX_NAV):

    ID = 0x01

    def __init__(self):
        pass


a = b'\xFF'
b = b'\xFF'

c = a + b
print(int.from_bytes(c,'big'))
print(256*256)
