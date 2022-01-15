    def sendData(self, data, chunkSize=1024):
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
                print('\t\x1b[1;31mHubo:\t'+str(Fails)+' errores\x1b[0m', end='')
                if Fails<10:
                    for i in range(10):
                        try:
                            n=int(con.recv(chunkSize).decode())
                            cache.append(data[chunkSize*n:chunkSize*(n+1)])
                            con.send(cache)
                            Fails=Fails-1
                        except:
                            pass
                else:
                    sent=False
                    break
            cache.clear()
        if sent:
            print("\x1b[1;32m"+'\t✔'+"\x1b[0m")
        return sent
 