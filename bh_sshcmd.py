#!python3

import threading
import paramiko
import subprocess

def ssh_command(ip, usr, psw, cmd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, password=psw, username=usr)
    ssh_session = client.get_transport().open_session()
    if (ssh_session.active):
        ssh_session.exec_command(cmd)
        print(ssh_session.recv(1024))
    return

ssh_command('localhost', 'kali', 'kali', 'id')