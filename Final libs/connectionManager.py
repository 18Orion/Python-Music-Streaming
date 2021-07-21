import socket, os
from time import sleep, localtime
from math import ceil

class connectionManager(object):
    def __init__(self, paralelCons=1, ip='192.168.1.27', port=2565):
        self.dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    #se conecta el socket con el ordendor central
        self.ip=(ip)
        self.port=(port)
        self.recibido=b''
        self.matriz=[]
        self.paralelCons=paralelCons

    #
    #Funciones de cliente
    #

    def tryConnect(self):
        """
        Función de conexión con el servidor
        """
        while True:
            try:
                self.dataSock=socket.socket()
                self.dataSock.connect((self.ip, self.port))
                break
            except:
                pass

    #
    #Funciones de servidor
    #

    def createServer(self):
        """
        Función de apertura del servidor
        """
        self.dataSock.setblocking(True)
        self.dataSock.settimeout(1)
        print('Abriendo servidor en la ip: {} puerto: {}'.format(*(self.ip,self.port)))
        while True:
            try:
                self.dataSock.bind((self.ip,self.port))
                self.dataSock.listen(self.paralelCons)
                break
            except (socket.timeout, socket.error, OSError):
                pass
        self.accepCons()

    def accepCons(self):
        """
        Función de conexión con el cliente
        """
        time=0
        print('Abriendo servidor y esperando conexion...',end='')
        self.dataSock.setblocking(True)
        self.dataSock.settimeout(1)
        while True:
            try:
                self.connection, self.client_address = self.dataSock.accept()
                self.passcode()
                print('\nConectado')
                self.dataSock.settimeout(None)
                break
            except (socket.timeout, socket.error):
                time=time+1
                print('\rAbriendo servidor y esperando conexion...\tTiempo transcurrido: ',time, 's', end='')

    #
    #Funciones de envío y recepción de datos
    #

    def recvData(self, bytesChunk=1024, preReturn=False, output=False):
        """
        Función de recibido de datos escalonado con función de cache en matriz 10*x
        """
        try:
            if self.connection:
                con=self.connection
        except:
            con=self.dataSock
        bytesChunkArray=[]
        self.matriz.clear()
        bytesError=[]
        chunkNumber=0
        chunkNumberError=0
        cache=b''
        a=0
        timeOuts=0
        con.setblocking(True)
        while con:
            con.settimeout(None)
            for i in range(10):
                try:
                    cache=con.recv(bytesChunk)
                    if cache:
                        bytesChunkArray.append(cache)
                    if con.getblocking()!=0.05:
                        con.settimeout(0.05)
                    cache=b''
                except socket.timeout: #el socket tiene error de timeout
                    timeOuts+=1
                except socket.error:        #el socket sufre un error al recibir
                    bytesError.append(i)
                    chunkNumberError+=1
            for i in range(len(bytesError)):
                try:
                    a=bytesError.pop(i)
                    con.send(str(a).encode())
                    cache=con.recv(bytesChunk)
                    bytesChunkArray.insert(a, cache)
                    chunkNumberError=chunkNumberError-1
                except:
                    pass
            if bytesChunkArray:
                self.matriz.append(list(bytesChunkArray))
                chunkNumber=chunkNumber+1
                if output:
                    print('Chunk numero '+str(chunkNumber)+'\t\t Packet(s) perdidos: '+str(chunkNumberError)+'\tTimeouts: '+str(timeOuts)+'\t Packet(s) recibidos '+str(len(bytesChunkArray)))
                bytesError.clear()
                timeOuts=0
            if preReturn:
                return bytesChunkArray
            else:
                if len(bytesChunkArray)<10:
                    break
            bytesChunkArray.clear()
        return self.matriz
    
    def streamData(self, bytesChunk=1024, preReturn=False, output=False):
        """
        Función de recepción de datos con menor tamaño de cache y sin almacenamiento a futuro.
        Modificar según el uso.
        Derivada de la función 'recvData'.
        """
        try:
            if self.connection:
                con=self.connection
        except:
            con=self.dataSock
        bytesChunkArray=[]
        self.matriz.clear()
        bytesError=[]
        chunkNumber=0
        chunkNumberError=0
        cache=b''
        a=0
        timeOuts=0
        con.setblocking(True)
        while con:
            con.settimeout(None)
            for i in range(10):
                try:
                    cache=con.recv(bytesChunk)
                    if cache:
                        bytesChunkArray.append(cache)
                    if con.getblocking()!=0.05:
                        con.settimeout(0.05)
                    cache=b''
                except socket.timeout: #el socket tiene error de timeout
                    timeOuts+=1
                except socket.error:        #el socket sufre un error al recibir
                    bytesError.append(i)
                    chunkNumberError+=1
            for i in range(len(bytesError)):
                try:
                    a=bytesError.pop(i)
                    con.send(str(a).encode())
                    cache=con.recv(bytesChunk)
                    bytesChunkArray.insert(a, cache)
                    chunkNumberError=chunkNumberError-1
                except:
                    pass
            if bytesChunkArray:
                chunkNumber=chunkNumber+1
                if output:
                    print('Chunk numero '+str(chunkNumber)+'\t\t Packet(s) perdidos: '+str(chunkNumberError)+'\tTimeouts: '+str(timeOuts)+'\t Packet(s) recibidos '+str(len(bytesChunkArray)))
                yield bytesChunkArray
                bytesError.clear()
                timeOuts=0
            else:
                if len(bytesChunkArray)<10:
                    break
            bytesChunkArray.clear()
               
    def sendData(self, data, chunkSize=1024, output=False):
        """
        Funcón de envio escalonado independiente del modo de uso de los datos y en el otro lado (stream o cache)
        """
        try:
            if self.connection:
                con=self.connection
        except:
            con=self.dataSock
        con.setblocking(True)
        con.settimeout(None)
        cache=[]
        Fails=0
        sent=True
        if output:
            print('\nEnviando',len(data),' bytes en ',ceil(len(data)/(chunkSize*10)), 'rondas', end='')
        for overall in range(ceil(len(data)/chunkSize)):
            con.settimeout(None)
            for i in range(10):
                cache.append(data[chunkSize*(overall*10+i):chunkSize*(overall*10+(i+1))])
            for i in range(10):
                try:
                    con.send(cache[i])
                except socket.error:
                    Fails+=1
            con.setblocking(True)
            con.settimeout(0.05)
            if Fails>0:
                if output:
                    print('\t\x1b[1;31mHubo:\t'+str(Fails)+' errores\x1b[0m', end='')
                if Fails<10:
                    for i in range(10):
                        try:
                            n=int(con.recv(chunkSize).decode())
                            cache.append(data[chunkSize*n:chunkSize*(n+1)])
                            con.send(cache)
                            Fails=Fails-1
                        except socket.timeout:
                            pass
                else:
                    sent=False
                    break
            cache.clear()
        if sent:
            if output:
                print("\x1b[1;32m"+'\t✔'+"\x1b[0m")
        return sent
 
    #VARIO

    def passcode(self):
        """
        Función de generación de un código de encriptación
        """
        try:
            time=localtime()
            code=ceil(int(str(time[0])+str(time[1])+str(time[2])+str(time[3])+str(time[4]))*int(self.ip.replace('.',''))/self.port)
            print('Connection from', self.ip,' port ', self.port,'with code:',code)
            return code
        except:
            pass