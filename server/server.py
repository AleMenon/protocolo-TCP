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
    # Tratamento de Erro: Verifica se arquivo existe
    if not os.path.exists(file_name):
        client.send('FILE_NOT_FOUND'.encode())
        print(f'Arquivo {file_name} não encontrado')
        return

    # Envia confirmação de início antes dos dados
    client.send('OK_START_SENDING'.encode())

    # Integridade: Cálculo do Hash SHA-256 do arquivo completo
    sha = hashlib.sha256()
    size = os.path.getsize(file_name)

    # Arquivos Grandes: Leitura em chunks (blocos) de 4096 bytes
    with open(file_name, 'rb') as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            sha.update(chunk)

    hash = sha.hexdigest()
    # Envia metadados: Hash (64 bytes) e Tamanho (8 bytes struct)
    client.send(hash.encode())
    client.send(struct.pack('!Q', size))

    # Transferência de Arquivo: Envio do conteúdo em chunks
    with open(file_name, 'rb') as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            client.sendall(chunk)    

    print('Arquivo enviado: ' + file_name)
    print('Hash: ' + hash)

def handle_message(client, string):
    # Chat: Armazena histórico e faz broadcast (envia para todos)
    messages.append(string)
    response = '\n'.join(messages) + '\nOK\n'
    client.sendall(response.encode())
    

def handle(client, address):
    # Thread dedicada: Loop de processamento de requisições
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            # Definição do Protocolo de Aplicação (Parsing)
            # Identifica se é Arquivo (GET) ou Chat (MESSAGE)
            if message.startswith('GET'):
                file_name = message.split()[1]
                handle_file(client, file_name)
            elif message.startswith('MESSAGE'):
                string = f'{address[0]}:{address[1]}: ' + ' '.join(message.split()[1:])
                handle_message(client, string)
            else:
                # Requisição "Sair" ou desconexão inesperada
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

        # Multithreading: Cria uma thread para cada cliente aceito
        thread = threading.Thread(target=handle, args=(client, address))
        thread.start()

print('Server ouvindo...')
receive()
