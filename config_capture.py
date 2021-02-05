#!/usr/bin/env python
import paramiko
import time
import re
import os
from datetime import date

def open_ssh_conn(ip,device_type,username,password,enable,newfile_dir):

    try:          
        session = paramiko.SSHClient()
        session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        session.connect(ip,username = username, password = password,look_for_keys=False)
        conn = session.invoke_shell()
        time.sleep(0.5)
        
        device_output = conn.recv(65535).decode()
        if re.search(">",device_output.split("\n")[-1]):
            hostname = re.findall("^(.*)>$",device_output.split("\n")[-1])[0]
            conn.send('enable\n')
            time.sleep(0.5)
            conn.send('%s\n'%enable)
            time.sleep(0.5)
        else:
            hostname = re.findall("^(.*)#$",device_output.split("\n")[-1])[0]
            
        if device_type == "router":
            selected_cmd_file = open('command_list_router.txt', 'r')
            selected_cmd_file.seek(0)
        elif device_type == "switch":
            selected_cmd_file = open('command_list_switch.txt', 'r')
            selected_cmd_file.seek(0)

        for each_line in selected_cmd_file.readlines():
            conn.send(each_line)
                time.sleep(0.5)
            
        selected_cmd_file.close()
        device_output = conn.recv(9999999).decode()
        
        if re.search('% Invalid input detected at', device_output):
            print('* There was at least one IOS syntax error on device %s' % ip)
        else:
            print('\nDONE for device %s (%s)'%(hostname,ip))
            
        new_f = open(newfile_dir+'\\'+hostname+'.txt','w+')
        new_f.write(device_output.decode())
        new_f.close()        
        session.close()

    except paramiko.AuthenticationException:
        print("\n* Invalid username or password for device %s (%s) \n* Please check the username/password file or the device configuration!"%(hostname,ip))
    
    except TimeoutError:
        print("\nConnection time out for Device %s (%s)"%(hostname,ip))

if __name__ == '__main__':
    device_list = open('device_list.txt','r')
    ip,device_type,username,password,enable = [],[],[],[],[]
    newfile_dir = "path/to/file/backupfile %s"%date.today().strftime("%d-%m-%Y")
    try:
        print("Creating new folder at %s"%newfile_dir)
        os.mkdir(newfile_dir)
    except FileExistsError:
        print("Folder %s Already Exists!"%newfile_dir)

    for x in range(len(device_list.readlines())):
        device_list.seek(0)
        ip.append(device_list.readlines()[x].split(',')[0].rstrip('\n'))
        device_list.seek(0)
        device_type.append(device_list.readlines()[x].split(',')[1].rstrip('\n'))
        device_list.seek(0)
        username.append(device_list.readlines()[x].split(',')[2].rstrip('\n'))
        device_list.seek(0)
        password.append(device_list.readlines()[x].split(',')[3].rstrip('\n'))
        device_list.seek(0)
        enable.append(device_list.readlines()[x].split(',')[4].rstrip('\n'))      
    device_list.close()

    for x in range(len(ip)):
        open_ssh_conn(ip[x],device_type[x],username[x],password[x],enable[x],newfile_dir)
