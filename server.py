import socket
import base64
import struct

HOST = 'localhost'
PORT = 3333

class Frame:
    def __init__(self, sync1, sync2, length, checksum, id_, flags, dados):
        self.sync1 = sync1
        self.sync2 = sync2
        self.length = length
        self.checksum = checksum
        self.id_ = id_
        self.flags = flags
        self.dados = dados

###### Montagem de quadro ######
#Recebe dado do console
data_frame = 0
data_lenght = 0

# fchecksum_string = hex(((sum(int(base64.b16encode(bytes(data_frame, 'str'))[i:i+2],16) for i in range(0, len(base64.b16encode(bytes(data_frame, 'str'))), 2))%0x100)^0xFF)+1)[2:]
fcheksum_int = 0

f_ACK = Frame(0xdcc023c2, 0xdcc023c2, data_lenght, fcheksum_int, 0, 0x80, data_frame)
cod = f'!IIHBBBB'

cdata = struct.pack(cod, f_ACK.sync1, f_ACK.sync2, f_ACK.length, f_ACK.checksum, f_ACK.id_, f_ACK.flags, f_ACK.dados)
print(cdata)
################################

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
print('Aguardando conexão de um cliente')
conn, ender = s.accept()

print('Conectado em', ender)
while True:
  data = conn.recv(1024)
  # Decodifica os dados
  data = base64.b16decode(data)
  
  if not data:
    print('Fechando conexão')
    conn.close()
    break
  
  print('Data recebida: ', data)
 
  # Desempacota
  udata = struct.unpack('!IIHBBB7s', data)
  print('Data unpacked: ', udata)

  #Mandando quadro de confirmação
  conn.sendall(base64.b16encode(cdata))
  
  # conn.sendall(data)