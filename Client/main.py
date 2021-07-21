import os
from lib.connectionManager import connectionManager
from lib.play import play
from sys import exit

def getNumber():
        i=input("Escoge la canción>> ")
        if i.isdigit():
            return int(i)-1
        else:
            print('No es un numero')
            return getNumber()

def selectSong(lista):
    listaCache=lista[0][0].decode()
    listaCache=listaCache.split(',')
    for i in range(len(listaCache)):
        if listaCache[i]:
            print(i+1, '.\t', listaCache[i])
    return listaCache[getNumber()].encode()

if __name__ == "__main__":
    play=play()
    os.system('clear')
    print("Abriendo conexion...")
    connectionManager = connectionManager()
    connectionManager.tryConnect()
    songs=[]
    while True:
        try:
            songs=connectionManager.recvData()
            if songs:
                connectionManager.sendData(selectSong(songs))
                a=connectionManager.recvData(1024, preReturn=True)
                if a:
                    a=a[0].decode().replace('(','').replace(')','').split(', ')
                play.importValues(int(a[0]),int(a[1]),int(a[2]))
                for i in connectionManager.streamData():
                    play.playSongfromList(i)
                connectionManager.sendData(b'finished')
        except KeyboardInterrupt:
            exit()