import os
import time

os.system('transmission-daemon')

dirs = {'/srv/cifs/games':['/srv/cifs/torrents/games/','games.txt'],
        '/srv/cifs/distros':['/srv/cifs/torrents/distros/','distros.txt'],
        '/srv/cifs/video':['/srv/cifs/torrents/video/','video.txt'],
        '/srv/cifs/other':['/srv/cifs/torrents/other/','other.txt'],
        '/srv/cifs/music':['/srv/cifs/torrents/music/','music.txt']}
fucking_shit = []  # Durty!!!

while True:
    for i in dirs:
        if os.path.isfile(dirs[i][0] + dirs[i][1]) is False:
            open(dirs[i][0] + dirs[i][1], 'w').close()
        file_data = open(dirs[i][0] + dirs[i][1], 'r')
        data = file_data.read().split('\n')
        file_data.close()
        dir_list = os.listdir(dirs[i][0])
        if fucking_shit != list(set(dir_list) - set(data[:-1])):
            file_data = open(dirs[i][0] + dirs[i][1], 'a')
            for k in list(set(dir_list) - set(data[:-1])):
                os.system('transmission-remote -w ' + i + ' -a ' '"' + dirs[i][0] + k + '"')
                file_data.write(k + '\n')
                file_data.flush()
            file_data.close()
    time.sleep(5)
