import socket
import base64
import struct

HOST = '127.0.0.1'
PORT = 3333

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

sync = str.encode('dcc023c2')
length = str.encode('0004')
chksum = str.encode('faef')
id_ = str.encode('00')
flags = str.encode('00')
dados = str.encode('01020304')

# Empacota
sdata = struct.pack('8s 8s 4s 4s 2s 2s 8s', sync, sync, length, chksum, id_, flags, dados)
print(sdata)

# Codifica
encode = base64.b16encode(sdata)
print('Dado encryptado: ', encode)

s.sendall(encode)
data = s.recv(1024)

print('Mensagem recebida: ', data.decode())