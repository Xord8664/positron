#!/bin/env python3

# ~ keys:
# ~ dir_to_download
# ~ torrents_location
# ~ list_location
# ~ invalid_list_location - TODO

#from datetime import datetime
import sys
import getopt
import configparser
import os
import time
import tempfile
import subprocess
import re

### Check config related things

try:
    opts, args = getopt.getopt(sys.argv[1:], 'c:')
except:
    sys.exit("use -c to specify config")

if len(opts) == 0:
    sys.exit("use -c to specify config")

for opt, arg in opts:
    if opt in ['-c']:
        config_file = arg

try:
    open(config_file, "r").readable()
    print('config = ' + config_file)
except:
    sys.exit("No such file or not readable")

read_conf = configparser.ConfigParser()
read_conf.read(config_file)

### Validate keys, check dirs and files

ini_ok = 0

for ini_section in read_conf:
    if ini_section != 'DEFAULT':
        if ('dir_to_download' in read_conf[ini_section]) and ('torrents_location' in read_conf[ini_section]) and ('list_location' in read_conf[ini_section]):
            print("Checking section " + ini_section + " :")
            try:
                test = tempfile.NamedTemporaryFile(dir=read_conf[ini_section]['dir_to_download'], prefix="transmission_check_")
                test.close            
                print('OK:' + read_conf[ini_section]['dir_to_download'])
            except:
                print('ERROR:' + read_conf[ini_section]['dir_to_download'])
                ini_ok += 1
                
            try:
                os.listdir(read_conf[ini_section]['torrents_location'])
                #os.access(read_conf[ini_section]['torrents_location'], os.R_OK | os.X_OK)
                print('OK:' + read_conf[ini_section]['torrents_location'])
            except:
                print('ERROR:' + read_conf[ini_section]['torrents_location'])
                ini_ok += 1
                
            try:
                open(read_conf[ini_section]['list_location'], 'r+').close
                print('OK:' + read_conf[ini_section]['list_location'])
            except:
                print('ERROR:' + read_conf[ini_section]['list_location'])
                ini_ok += 1
        else:
            print("param dir_to_download or torrents_location or list_location not exist in section" + ini_section)
            ini_ok += 1
        sys.stdout.flush()
if ini_ok > 0:
    sys.exit("Could not find param config or permissions/IO errors")

### Set up security parameters for connection with transmission-daemon and other in [DEFAULT] section
### This breaks subprocess.run

#if len(read_conf['DEFAULT']) > 0:
#    for ini_key in read_conf['DEFAULT']:
#        if ini_key == 'user':
#            print('user = ' + read_conf['DEFAULT']['user'])
#            transmission_user = read_conf['DEFAULT']['user']
#        elif ini_key == 'pass':
#            print('password = ' + read_conf['DEFAULT']['pass'])
#            transmission_pass = read_conf['DEFAULT']['pass']
#        else:
#            print(read_conf['DEFAULT'][ini_key] + ' unknown. Ignoring')
#    if transmission_user != '' and transmission_pass != '':
#        auth = '-n ' + transmission_user + ':' + transmission_pass
#    else:
#        print('WARNING: user or pass parameters is empty. Authentication will not be used!')
#        auth = ''
#else:
#    print('WARNING: section "DEFAULT" is empty. Authentication will not be used!')
#    auth = ''

### Main functional

# need to handle "invalid or corrupt torrent file"

torrent_file_pattern = re.compile('.+\.torrent', re.IGNORECASE)

while True:
    for ini_section in read_conf:
        if ini_section != 'DEFAULT':
            torrents_list = []
            read_torrents_list = open(read_conf[ini_section]['list_location'], 'r')
            added_torrents = read_torrents_list.read().split('\n')
            read_torrents_list.close()
            dir_list = os.listdir(read_conf[ini_section]['torrents_location'])
            for _file_ in dir_list:
                m = torrent_file_pattern.match(_file_)
                if m:
                    #print("in dir: " + m.group())
                    torrents_list.append(m.group())
            #for debug1 in added_torrents : print("in file: " + debug1)
            #print("dir: " + ' '.join(map(str, torrents_list)))
            #print("file: " + ' '.join(map(str,added_torrents)))
            if list(set(torrents_list) - set(added_torrents[:-1])) != []: #[:-1] because last element is '\n'
                for torrent_file in list(set(dir_list) - set(added_torrents[:-1])):
                    #print(torrent_file)
                    torrent_file_path = read_conf[ini_section]['torrents_location'] + '/' + torrent_file
                    print("Found new torrent file: " + torrent_file_path)
                    try:
                        cmd = subprocess.run(['/usr/bin/transmission-remote', '-w', read_conf[ini_section]['dir_to_download'], '-a', torrent_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', timeout=60)
                        print("stdout: \n" + cmd.stdout)
                        print("stderr: \n" + cmd.stderr)
                        print("exit code: " + str(cmd.returncode))
                        #print("debug: cmd")
                        #debug_var1 = True
                    except subprocess.TimeoutExpired:
                        sys.exit("Timeout expired. Check transmission daemon status and overall system health")
                    if  cmd.returncode == 0:
                        write_torrent_list = open(read_conf[ini_section]['list_location'], 'a')
                        write_torrent_list.write(torrent_file + '\n') # always append new line
                        write_torrent_list.flush()
                        write_torrent_list.close()
                    elif 'invalid or corrupt torrent file' in cmd.stdout:  # TODO
                        print("Need to delete " + torrent_file_path)
    #print(datetime.now().time())
    sys.stdout.flush()
    time.sleep(5)
