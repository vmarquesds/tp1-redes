import socket
import base64
import struct

HOST = 'localhost'
PORT = 3333

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
  print('Data recebida: ', data)
  
  if data:
    # Desempacota
    udata = struct.unpack('8s 8s 4s 4s 2s 2s 8s', data)
    print('Data unpacked: ', udata)  

  if not data:
    print('Fechando conexão')
    conn.close()
    break
  conn.sendall(data)