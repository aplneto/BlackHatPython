#!python3
import sys
import socket
import threading

def usage():
    msg = (
        "Black Hat Python's Proxy Tool\n"
        "Usage: proxy.py [local_host] [local_port] [remote_host] [remote_port] "
        "[receive_first]\n"
        "Example: proxy.py 127.0.0.1 8080 10.12.123.1 9000 True"
    )
    print(msg)
    sys.exit(0)

def server_loop(local_host, local_port, remote_host, remote_port, rcv_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local_address = (local_host, local_port)

    try:
        server.bind(local_address)
    except:
        print("Failed to lisetn on %s:%d" % local_address, file=sys.stderr)
        sys.exit(14)
    
    print("Listening on %s:%d" % local_address)

    server.listen(5)

    while True:
        client, addr = server.accept()
        print("Connection received from %s:%d" % addr)
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client, remote_host, remote_port, rcv_first)
        )
        proxy_thread.start()

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_address = (remote_host, remote_port)
    remote_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_connection.connect(remote_address)

    if receive_first:
        remote_buffer = receive_from(remote_connection)
        hexdump(remote_buffer)
        remote_buffer = response_handler(remote_buffer)

        if len(remote_buffer):
            print("[<==] Sending %d bytes to localhost" % len(remote_buffer))
            client_socket.send(remote_buffer)
    
    while True:
        error_count = 0
        local_buffer = receive_from(client_socket)

        if len(local_buffer):
            print("[==>] Recived %d bytes from localhost" % len(local_buffer))
            hexdump(local_buffer)
            local_buffer = request_handler(local_buffer)
            remote_connection.send(local_buffer)
            print("[==>] Sent to remote")
        
        remote_buffer = receive_from(remote_connection)
        if len(remote_buffer):
            print("[<==] Sending %d bytes to localhost" % len(remote_buffer))
            hexdump(remote_buffer)
            
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost")
        
        if not (len(local_buffer) and len(remote_buffer)):
            client_socket.close()
            remote_connection.close()
            print("[*] Closing connections")
            break

def receive_from(connection, timeout=2):
    buffer = b''
    connection.settimeout(timeout)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except:
        pass

    return buffer


def hexdump(buffer, length=16):
    results = []
    hex_buffer = buffer.hex()
    for i in range(0, len(hex_buffer), length):
        hex = hex_buffer[i:i+length]
        hex = " ".join(hex[n:n+2] for n in range(0, len(hex), 2))
        text = bytes.fromhex(hex_buffer[i:i+length]).decode()
        results.append('%04X %-*s %s' % (i, length + 8, hex, text))
    print('\n'.join(results))

def response_handler(buffer):
    '''
    Function to perform packet modifications
    '''
    return buffer

def request_handler(buffer):
    '''
    Function to perform packet modifications
    '''
    return buffer

def main():
    if len(sys.argv[1:]) != 5:
        usage()
    
    local_host, local_port, remote_host, remote_port, rcv_first = sys.argv[1:]
    local_port = int(local_port)
    remote_port = int(remote_port)
    rcv_first = (rcv_first == "True")
    if rcv_first:
        print("Receiving first")

    server_loop(local_host, local_port, remote_host, remote_port, rcv_first)

if __name__ == '__main__':
    main()
