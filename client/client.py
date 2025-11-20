import threading
import socket
import hashlib
import struct

SERVER_IP = 'localhost'
SERVER_PORT = 8000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, SERVER_PORT))

def receive_message():
    buffer = ''
    while True:
        buffer = client.recv(4096).decode('ascii')
        if buffer.endswith('OK\n'):
            break

    buffer = buffer[:-3]

    print('Mensagens: ')
    print(buffer)

def receive_file(file_name):
    response = client.recv(64).decode('ascii')
    if response == 'FILE_NOT_FOUND':
        raise FileNotFoundError('Arquivo não encontrado pelo servidor')

    expected_hash = client.recv(64).decode()
    size = struct.unpack('!Q', client.recv(8))[0]

    received = b''
    while len(received) < size:
        chunk = client.recv(4096)
        if not chunk:
            break
        received += chunk

    sha = hashlib.sha256()
    sha.update(received)
    final_hash = sha.hexdigest()

    if expected_hash != final_hash:
        raise Exception(f'Hashes diferentes - Esperado: {expected_hash} - Recebido: {final_hash}')

    with open(file_name, 'wb') as f:
        f.write(received)
    print("Arquivo recebido com sucesso")

def send():
    while True:
        try:
            message = input('Escolha o tipo de comunicação (Sair, Arquivo [file_name], Chat [Mensagem]): ')
            if message.startswith('Sair'):
                print('Encerrando comunicação com o servidor')
                client.close()
                break
            elif message.startswith('Arquivo'):
                file = 'GET ' + message.split()[1]
                client.sendall(file.encode())
                receive_file(message.split()[1])
            elif message.startswith('Chat'):
                chat = 'MESSAGE ' + ' '.join(message.split()[1:])
                client.sendall(chat.encode())
                receive_message()
            else:
                print(f'Método de comunicação inválido: {message}')
                print('Opções são (Sair, Arquivo [file_name], Chat [Mensagem])')
        except Exception as e:
            print(f'Erro na comunicação com o servidor: {e}')
            client.close()

receive_thread = threading.Thread(target=send)
receive_thread.start()
