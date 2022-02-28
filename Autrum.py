import numpy as np 
import pyaudio as pa 
import struct 
import matplotlib.pyplot as plt
import array as ar

import time

#Numero de fotogramas en la cual se dividen las senales
CHUNK = 2048

#Me ayuda a establece que tan buena es una muestra de audio (Bit depth)
FORMAT = pa.paInt16  #El mejor que soporta este equipo es el de 16 y el paALSA (Solo Linux)
            #El de 8 bits genera distorsion 
            #El de 16bits (96db) es el que mas se utiliza, hace que se escuche mejor
            #El de 24bits es el que se usa actualmente y es mejor.
            #Esta de 32bits pero es muy alto para usarlo

#Numero de canales de entrada a usar
CHANNELS = 1 #Se usa uno ya que esto depende de la cantidad de microfonos que posee el equipo.

#El RATE es la frecuencia de muestreo, o sea, el numero de muestras por una unidad de tiempo
RATE = 44100 # (En HZ) Esta da una buena calidad, es la que normalemnte se usa (estandar)
             # La de 48000 da una calidad casi de estudio, (muy buena).


#Creacion de clase de PyAudio
p = pa.PyAudio()


#def graficarSenal():

#Esta funcion me toma una senal por medio del microfono y la mete una parte en un chunk
def tomarSenalPorStream():
    
    
    #Tomo la senal captada por el microfono, tomo un fracmento.
    toma = p.open(
        format = FORMAT,
        channels = CHANNELS,
        rate = RATE,
        input=True,
        output=True,
        frames_per_buffer=CHUNK) 


    #Basicamente son dos graficos diferentes, el 2 significa 2 filas. Fig es la pantalla donde se encuentran.
    fig, (ax1,ax2) = plt.subplots(2) 

    #Me devuelve una lista dentro de un intervalo
    x_frecuencia = np.arange(0,2*CHUNK,2) #[0,2,4,6,....,2048]
    x_furier = np.linspace(0, RATE, CHUNK) #[0,1024,2048,....,RATE]
    print(x_frecuencia)
    print(x_furier)

    #Coloco titulo a cada uno
    ax1.set_title('Frecuencia')
    ax2.set_title('Furier')

    #Establezco los limites de cada grafico
    ax1.set_xlim(0, CHUNK)
    ax1.set_ylim(-40000, 40000)

    ax2.set_xlim(20, RATE)
    #La salida de los calculos de furier varian de 0 a 1, meto -1 para verla mejor
    ax2.set_ylim(-1, 1)

    line_frecuencia, = ax1.plot(x_frecuencia, np.random.rand(CHUNK),'r')
    #La representacion de frecuencia siempre se hace en graficos semilogaritmicos
    line_furier, = ax2.semilogx(x_furier, np.random.rand(CHUNK), 'b')
    
    fig.show()

    
    while 1:
        data = toma.read(CHUNK)
        dataInt = struct.unpack(str(CHUNK) + 'h', data)

        line_frecuencia.set_ydata(dataInt)
        #aca trasnformamos la senal con furier
        line_furier.set_ydata(np.abs(np.fft.fft(dataInt))*2/(11000*CHUNK))
        
        fig.canvas.draw()
        fig.canvas.flush_events()

tomarSenalPorStream()



