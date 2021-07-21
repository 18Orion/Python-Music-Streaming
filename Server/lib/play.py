import pyaudio, wave, os
from pydub import AudioSegment

class play(object):
    def __init__(self, chunk=1024):
        self.chunk=chunk
        self.playInterface = pyaudio.PyAudio()

    def convertToWav(self, nombre):   #Convierte archivo mp3 a wav
        if os.path.isfile(nombre):
            sound = AudioSegment.from_file(nombre, format='mp3')
            sound.export(nombre.replace('.mp3', '.wav'), format='wav')
            return nombre.replace('.mp3', '.wav')

    def setParameters(self, wf):
        stream = self.playInterface.open(format = self.playInterface.get_format_from_width(wf.getsampwidth()),    #setea los parametros de reproducción
                channels = wf.getnchannels(),
                rate = wf.getframerate(),
                output = True)
        return stream

    def playRecording(self, nombre):             #Reproduce un sonido +=
        if os.path.isfile(nombre):
            wf = wave.open(self.convertToWav(nombre), 'rb')
            stream=self.setParameters(wf)
            data = wf.readframes(self.chunk)
            while data != '':
                stream.write(data)
                data = wf.readframes(self.chunk)
            stream.close()
            self.playInterface.terminate()

    def returnParameters(self, nombre):
        if os.path.isfile(nombre):
            wf = wave.open(self.convertToWav(nombre), 'rb')
            recordFormat= self.playInterface.get_format_from_width(wf.getsampwidth())
            channels=channels = wf.getnchannels()
            rate = wf.getframerate()
            return recordFormat, channels, rate

    def readSong(self, nombre, Stream=False):
        if os.path.isfile(nombre):
            wf = wave.open(self.convertToWav(nombre), 'rb')
            data=b''
            cache=b''
            cache = wf.readframes(self.chunk)
            while cache:
                for i in range(10):
                    data=data+cache
                    cache = wf.readframes(self.chunk)
                if Stream:
                    yield data
                    data=b''
            if not Stream:
                return data

    def importValues(self, recordFormat, channelPref, frameRate):
        self.stream = self.playInterface.open(format = recordFormat, channels = channelPref, rate = frameRate, output = True)

    def playSongfromList(self, lista):
        for i in range(len(lista)):
            try:
                self.stream.write(lista[i])
            except KeyboardInterrupt:
                exit()
            except:
                pass
        