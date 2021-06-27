import binascii, struct, base64

class Frame:
    def __init__(self, sync1=0, sync2=0, length=0, checksum=0, id_=0, flags=0, dados=0):
        self.sync1 = sync1
        self.sync2 = sync2
        self.length = length
        self.checksum = checksum
        self.id_ = id_
        self.flags = flags
        self.dados = dados

def checksum(info):
    s = 0
    for i in range(0, len(info), 4):
        s += int(info[i:i+4], 16)
        if len(hex(s)) > 6:
            s = (int(hex(s)[2], 16) + int(hex(s)[3:], 16))
    return s ^ 0xFFFF

def fill_checksum(frame):
    cod = f'!IIHHBB{frame.length}s'
    # Empacota
    print('fchecksum1: ', frame.checksum)
    dt = struct.pack(cod, frame.sync1, frame.sync2, frame.length, frame.checksum, frame.id_, frame.flags, frame.dados)
    frame.checksum = checksum(binascii.b2a_hex(dt).decode())
    print('fchecksum2: ', frame.checksum)
    return frame


f = Frame(0xdcc023c2, 0xdcc023c2, 0, 0, 0, 0x80, str.encode(''))
f = fill_checksum(f)
print(f)
sdata = struct.pack(f'!IIHHBB{f.length}s', f.sync1, f.sync2, f.length, f.checksum, f.id_, f.flags, f.dados)
print(sdata)
sdata = base64.b16encode(sdata)
print(sdata)

