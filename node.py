import socket, base64, struct, sys, time, binascii
from typing import Type

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
    dt = struct.pack(cod, frame.sync1, frame.sync2, frame.length, frame.checksum, frame.id_, frame.flags, frame.dados)
    frame.checksum = checksum(binascii.b2a_hex(dt).decode())
    return frame


def frame_mount(config, id_=0, flag=0):
    data_frame = config.input_
    cod = f'!IIHHBB7s'

    if flag == 'end':
        f = Frame(0xdcc023c2, 0xdcc023c2, 0, 0, id_, 0x40, str.encode('1234567'))
        f = fill_checksum(f)
        ENDdata = struct.pack(cod, f.sync1, f.sync2, f.length, f.checksum, f.id_, f.flags, f.dados)
        # print(ENDdata)

        return ENDdata
    if flag == 'ack':
        f = Frame(0xdcc023c2, 0xdcc023c2, 0, 0, id_, 0x80, str.encode('1234567'))
        f = fill_checksum(f)
        ACKdata = struct.pack(cod, f.sync1, f.sync2, f.length, f.checksum, f.id_, f.flags, f.dados)
        # print(ACKdata)

        return ACKdata
    

    data_len = len(data_frame)
    f = Frame(0xdcc023c2, 0xdcc023c2, data_len, 0, id_, 0, str.encode(data_frame))
    f = fill_checksum(f)
    sdata = struct.pack(f'!IIHHBB{f.length}s', f.sync1, f.sync2, f.length, f.checksum, f.id_, f.flags, f.dados)

    return sdata

def frame_unmount(data):
    udata = struct.unpack('!IIHHBB7s', data)
    frame = Frame(udata[0], udata[1], udata[2], udata[3], udata[4], udata[5], udata[6])
    # print('dado desempacotado: ', hex(frame.flags))

    return frame

def check_chksum(frame):
    aux = frame.checksum
    frame.checksum = 0
    aux2 = fill_checksum(frame).checksum
    if aux == aux2:
        return True
    else:
        return False
        


def send_msg_mult_pckg(s, config):
    totalsent = 0
    id_ = 0
    # input_ = open(f'{config.input_}.txt')
    chunk_size = int(7)
    msg = []
    with open(f'{config.input_}.txt') as fh:
        while (contents := fh.read(chunk_size)):
            count = 0
            if len(contents) < chunk_size:
                while (chunk_size - len(contents)):
                    contents = contents[:len(contents)] + ' '
                    print(contents, len(contents), chunk_size - len(contents))
                    count += 1
            msg.append(contents)
    # print(msg)

    while totalsent < len(msg):
        config.input_ = msg[totalsent]
        id_ = 1 - id_

        sdata = frame_mount(config, id_)
        encode = base64.b16encode((sdata))
        s.send(encode)

        totalsent = totalsent + 1
        
        s.settimeout(2)
        try:
            rdata = s.recv(1024)
            rdata = base64.b16decode(rdata)
            unmtpacket = frame_unmount(rdata)

            if not check_chksum(unmtpacket):
                totalsent = totalsent - 1
                raise TypeError('id dif')

            if unmtpacket.id_ != id_:
                totalsent = totalsent - 1
                raise TypeError('id dif')
        except:
            totalsent = totalsent - 1
            continue

        print('Mensagem recebida: ', rdata)
    
    ENDframe = base64.b16encode(frame_mount(Configs(), 0, 'end'))
    s.send(ENDframe)
    print('Fim')

def receive_msg(s, conn):
    output = open(f'{config.output_}.txt', 'a+')
  # print(config.input_)

    while True:
        # time.sleep(1)
        s.settimeout(2)
        try:
            data = conn.recv(1024)
            data = base64.b16decode(data)
            unmtpacket = frame_unmount(data)

            if not check_chksum(unmtpacket):
                totalsent = totalsent - 1
                raise TypeError('id dif')
        except:
            print('Acabou o tempo', data)
        # Decodifica os dados
        
        if not data:
            print('Fechando conexão')
            conn.close()
            break
        
        print('Data recebida: ', data)

        # Desempacota
        udata = struct.unpack('!IIHHBB7s', data)
        print('Data unpacked: ', udata)

        if udata[5] == 64:
            conn.sendall(base64.b16encode(frame_mount(Configs(), 0, 'end')))
            time.sleep(1)
            print('Encerrando conexão')
            sys.exit(1)
        
        output.write(udata[6].decode())

        ACKframe = base64.b16encode((frame_mount(Configs(), udata[4], 'ack')))

        #Mandando quadro de confirmação
        conn.sendall(ACKframe)
    output.close()

if __name__ == '__main__':
    
    if len(sys.argv) == 6:
        s, config = set_sock(sys.argv)
        send_msg_mult_pckg(s, config)
    else:
        s, config, conn, ender = set_sock(sys.argv)
        receive_msg(s, conn)