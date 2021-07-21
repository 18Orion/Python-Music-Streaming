import socket, os, sys
from time import localtime, sleep
from math import ceil
from random import randint
from lib.connectionManager import connectionManager
from lib.play import play
from sys import exit

def listSong():
    pathList=os.listdir('Canciones')
    cache=''
    for i in range(len(pathList)):
        if pathList[i] and '.mp3' in pathList[i]:
            cache+=pathList[i]+','
    return cache

if __name__ == "__main__":
    play=play()
    os.system('clear')
    connectionManager=connectionManager()
    connectionManager.createServer()
    song=''
    wait=[]
    while True:
        os.system('clear')
        connectionManager.sendData(listSong().encode())
        while True:
            try:
                song=connectionManager.recvData()
                if song:
                    song=song[0][0].decode()
                    print(song)
                    nombre=play.convertToWav(os.getcwd()+'/Canciones/'+song)#os.getcwd()+'/Canciones/'+song.decode()
                    connectionManager.sendData(str(play.returnParameters(nombre)).encode())
                    for i in play.readSong(nombre, True):
                        connectionManager.sendData(i, output=True)
                    song=''
                    while True:
                        wait=connectionManager.recvData()
                        if wait:
                            wait.clear()
                            break  
            except KeyboardInterrupt:
                exit()
