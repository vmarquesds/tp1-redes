import socket, base64, struct, sys, time

class Frame:
    def __init__(self, sync1=0, sync2=0, length=0, checksum=0, id_=0, flags=0, dados=0):
        self.sync1 = sync1
        self.sync2 = sync2
        self.length = length
        self.checksum = checksum
        self.id_ = id_
        self.flags = flags
        self.dados = dados
class Configs:
    def __init__(self, id_flag=0, port_=0, input_=0, output_=0, ip_=0):
        self.id_flag = id_flag
        self.port_ = port_
        self.input_ = input_
        self.output_ = output_
        self.port_ = port_
        self.ip_ = ip_


def set_sock(args):
    config = Configs()
    if len(args) == 6:    
        config.id_flag = args[1]
        config.ip_ = args[2]
        config.port_ = args[3]
        config.input_ = args[4]
        config.output_ = args[5]
        HOST = '127.0.0.1'
        PORT = int(config.port_)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))

        return s, config
    else: 
        config.id_flag = args[1]
        config.port_ = args[2]
        config.input_ = args[3]
        config.output_ = args[4]
        HOST = 'localhost'
        PORT = int(config.port_)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen()
        print('Aguardando conexão de um cliente')
        conn, ender = s.accept()

        return s, config, conn, ender


def frame_mount(config, id_=0):
    data_frame = config.input_
    cod = f'!IIHBBB7s'

    if config.id_flag == 'end':
        f = Frame(0xdcc023c2, 0xdcc023c2, 0, 0, 0, 0x40, str.encode('1234567'))
        ENDdata = struct.pack(cod, f.sync1, f.sync2, f.length, f.checksum, f.id_, f.flags, f.dados)
        # print(ENDdata)

        return ENDdata
    if data_frame == 0:
        f = Frame(0xdcc023c2, 0xdcc023c2, 0, 0, 0, 0x80, str.encode('1234567'))
        ACKdata = struct.pack(cod, f.sync1, f.sync2, f.length, f.checksum, f.id_, f.flags, f.dados)
        # print(ACKdata)

        return ACKdata
    

    data_len = len(data_frame)
    fchecksum_str = hex(((sum(int(base64.b16encode(bytes(data_frame, 'ascii'))[i:i+2],16) for i in range(0, len(base64.b16encode(bytes(data_frame, 'ascii'))), 2))%0x100)^0xFF)+1)[2:]
    fcheksum_int = int(fchecksum_str, 16)

    f = Frame(0xdcc023c2, 0xdcc023c2, data_len, fcheksum_int, id_, 0, str.encode(data_frame))
    cod = f'!IIHBBB{data_len}s'

    # Empacota
    sdata = struct.pack(cod, f.sync1, f.sync2, f.length, f.checksum, f.id_, f.flags, f.dados)
    # print(sdata)

    return sdata

def frame_unmount(data):
    udata = struct.unpack('!IIHBBB7s', data)
    frame = Frame(udata[0], udata[1], udata[2], udata[3], udata[4], udata[5], udata[6])
    # print('dado desempacotado: ', hex(frame.flags))

    return frame

def frame_ACKm(config):
    return frame_mount(config)

def frame_ENDm(config):
    config.id_flag = 'end'
    return frame_mount(config)


def encode16(data):
    encode = base64.b16encode(data)
    # print('Dado encryptado: ', encode)

    return encode

def decode16(data):
    decode = base64.b16decode(data)
    
    return decode

ACKframe = encode16(frame_ACKm(Configs()))
ENDframe = encode16(frame_ENDm(Configs()))

def send_msg_mult_pckg(s, config):
    totalsent = 0
    id_ = 0
    input_ = open(f'{config.input_}.txt', 'r+')
    msg = input_.readlines()
    print(msg)

    while totalsent < len(msg):

        config.input_ = msg[totalsent]
        id_ = 1 - id_

        sdata = frame_mount(config, id_)
        encode = encode16(sdata)
        sent = s.send(encode)
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent = totalsent + 1
        
        s.settimeout(2)
        try:
            rdata = s.recv(1024)
            rdata = decode16(rdata)
            unmtpacket = frame_unmount(rdata)
        except:
            totalsent = totalsent - 1
            continue

        print('Mensagem recebida: ', rdata)
            
        # if unmtpacket.flags == 128:
        #     edata = encode16(ENDframe)
        #     s.sendall(edata)
        #     # time.sleep(1)
        #     print('Fim da conexão')
        #     sys.exit(1)
    
    s.send(ENDframe)
    print('Fim')

if __name__ == '__main__':
    
    s, config = set_sock(sys.argv)
    send_msg_mult_pckg(s, config)