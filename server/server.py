import threading
import socket
import hashlib
import os
import struct

IP_ADDRESS = 'localhost'
PORT = 8000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((IP_ADDRESS, PORT))
server.listen()

messages = []

def handle_file(client, file_name):
    if not os.path.exists(file_name):
        client.send('FILE_NOT_FOUND'.encode())
        print(f'Arquivo {file_name} não encontrado')
    client.send('OK_START_SENDING'.encode())

    sha = hashlib.sha256()
    size = os.path.getsize(file_name)

    with open(file_name, 'rb') as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            sha.update(chunk)

    hash = sha.hexdigest()
    client.send(hash.encode())
    client.send(struct.pack('!Q', size))

    with open(file_name, 'rb') as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            client.sendall(chunk)    

    print('Arquivo enviado: ' + file_name)
    print('Hash: ' + hash)

def handle_message(client, string):
    messages.append(string)
    response = '\n'.join(messages) + '\nOK\n'
    client.sendall(response.encode())
    

def handle(client, address):
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message.startswith('GET'):
                file_name = message.split()[1]
                handle_file(client, file_name)
            elif message.startswith('MESSAGE'):
                string = f'{address[0]}:{address[1]}: ' + ' '.join(message.split()[1:])
                handle_message(client, string)
            else:
                client.close()
                print(f'Cliente {address} desconectado')
                break
        except Exception as e:
            print(f'Erro interno do servidor: {e}')
            client.close()

def receive():
    while True:
        client, address = server.accept()
        print(f'Conectado com {str(address)}')

        thread = threading.Thread(target=handle, args=(client, address))
        thread.start()

print('Server ouvindo...')
receive()
