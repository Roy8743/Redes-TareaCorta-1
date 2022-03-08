import numpy as np
import pyaudio as pa
import struct
import matplotlib.pyplot as plt
import array as ar
import wave
import threading
import os
from pynput import keyboard as kb
import time
import pickle
import math

iniciar = 0
detener = 0
pausa = 0
savedData = []
filename = ""

# Numero de fotogramas en la cual se dividen las senales
chunk_size = 2048  # tomo 2048 y proceso, luego tomo otros 2048 y asi sucesivamente

# Me ayuda a establece que tan buena es una muestra de audio (Bit depth)
FORMAT = pa.paInt16  # El mejor que soporta este equipo es el de 16 y el paALSA (Solo Linux)

# El de 8 bits genera distorsion
# El de 16bits (96db) es el que mas se utiliza, hace que se escuche mejor
# El de 24bits es el que se usa actualmente y es mejor.
# Esta de 32bits pero es muy alto para usarlo y nadie lo usa

# Numero de canales de entrada a usar
CHANNELS = 1  # Se usa uno ya que esto depende de la cantidad de entradas de audio que posee el equipo.

# El RATE es la frecuencia de muestreo, o sea, el numero de muestras por una unidad de tiempo
RATE = 44100  # (En HZ) Esta da una buena calidad, es la que normalemnte se usa (estandar)
# La de 48000 da una calidad casi de estudio, (muy buena) pero depende del equipo.


# Creacion de clase de PyAudio
p = pa.PyAudio()


def pulsa(tecla):
    if tecla == kb.KeyCode.from_char('i'):
        print("Se ha presionado la tecla iniciar grabacion")
    elif tecla == kb.KeyCode.from_char('p'):
        print('Se ha presionado la tecla pr/reanudar')
    elif tecla == kb.KeyCode.from_char('q'):
        print("Se ha pulsado la tecla detener")


def suelta(tecla):
    global detener
    global iniciar
    global pausa

    # p = 'p'  # Para pr o reanudar
    # d = 'q'  # Para detener de grabar
    # ini = 'i'  # Para iniciar a grabar

    # Se presiona el boton de inicar grabacion
    if tecla == kb.KeyCode.from_char('i'):
        # Si no esta iniciada, iniciela
        if iniciar == 0:
            iniciar = 1

    # Se presiona el boton de detener grabacion
    elif tecla == kb.KeyCode.from_char('d'):
        if iniciar == 1:
            # pr = 0
            detener = 1

    # Se presiona el boton de pausa/reanudar
    elif tecla == kb.KeyCode.from_char('p'):
        if iniciar == 1:
            pausa = pausa ^ 1

def Analizador():
    # Esta funcion me toma una senal por medio del microfono y la mete una parte en un chunk

    frames = []  # Esto me ayuda a guardar los cuadros de la grabacion

    dataOrginal = []
    dataFourier = []

    global detener
    global iniciar
    global pausa
    global savedData

    escuchador = kb.Listener(pulsa, suelta)
    escuchador.start()

    # Tomo la senal captada por el microfono, tomo un fracmento.
    entradaDeMic = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        output=True,
        frames_per_buffer=chunk_size)

    # Basicamente son dos graficos diferentes, el 2 significa 2 filas. Fig es la pantalla donde se encuentran.
    fig, (ax1, ax2) = plt.subplots(2)

    # Me devuelve una lista dentro de un intervalo
    x_frecuencia = np.arange(0, 2 * chunk_size, 2)  # [0,2,4,6,....,2048]
    x_fourier = np.linspace(0, RATE, chunk_size)  # [0,1024,2048,....,RATE]

    # Coloco titulo a cada uno
    ax1.set_title('Frecuencia')
    ax2.set_title('Fourier')
    # Establezco los limites de cada grafico
    ax1.set_xlim(0, chunk_size)
    ax1.set_ylim(-40000, 40000)

    ax2.set_xlim(20, RATE + 200)
    # La salida de los calculos de fourier varian de 0 a 1, meto -1 para verla mejor
    ax2.set_ylim(0, 2)

    line_frecuencia, = ax1.plot(x_frecuencia, np.random.rand(chunk_size), color='r')
    # La representacion de frecuencia siempre se hace en graficos semilogaritmicos
    line_fourier, = ax2.semilogx(x_fourier, np.random.rand(chunk_size), color='b')

    fig.show()

    while escuchador.is_alive():

        if pausa:
            # Tengo que dejar de tomar el stream, lo cierro de una
            entradaDeMic.stop_stream()
            while pausa:
                line_frecuencia.set_ydata(dataOrginal)
                # aca trasnformamos la senal con fourier
                line_fourier.set_ydata(np.abs(np.fft.fft(dataOrginal)) * 2 / (11000 * chunk_size))

                fig.canvas.draw()
                fig.canvas.flush_events()
            # vuelvo a abrir el stream
            entradaDeMic = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=True,
                                  frames_per_buffer=chunk_size)
            continue

        data = entradaDeMic.read(chunk_size)

        if iniciar:
            frames.append(data)  # Guardo o grabo los cuadros
        dataOrginal = struct.unpack(str(chunk_size) + 'h', data)
        # Se traducen los bits a datos interpretados dado el formato del parametro 1

        line_frecuencia.set_ydata(dataOrginal)

        # aca trasnformamos la senal con fourier
        temp_ft = np.abs(np.fft.fft(dataOrginal)) * 2 / (11000 * chunk_size)
        if iniciar:
            savedData.append([temp_ft, dataOrginal])
        line_fourier.set_ydata(temp_ft)

        fig.canvas.draw()
        fig.canvas.flush_events()

        if detener:
            entradaDeMic.stop_stream()
            entradaDeMic.close()
            p.terminate()
            escuchador.stop()
            guardarGrabacion(frames)


def guardarGrabacion(frames):
    # Guardo el audio grabado
    # os.system("clear")
    global filename
    n = input("Ingrese el nombre del archivo a guardar: ")
    filename = n + ".atm"
    dbfile = open(filename, 'ab')
    n = n + '.wav'
    gb = wave.open(n, 'wb')
    gb.setnchannels(CHANNELS)
    gb.setsampwidth(p.get_sample_size(FORMAT))
    gb.setframerate(RATE)
    gb.writeframes(b''.join(frames))
    gb.close()
    plt.close()

    db = [savedData]
    pickle.dump(db, dbfile)


Analizador()


def Reproductor():
    dbfile = open(filename, 'rb')
    db = pickle.load(dbfile)
    dbfile.close()

    # Basicamente son dos graficos diferentes, el 2 significa 2 filas. Fig es la pantalla donde se encuentran.
    fig2, (ax1, ax2) = plt.subplots(2)
    fig2.canvas.flush_events()

    # Me devuelve una lista dentro de un intervalo
    x_frecuencia = np.arange(0, 2 * chunk_size, 2)  # [0,2,4,6,....,2048]
    x_furier = np.linspace(0, RATE, chunk_size)  # [0,1024,2048,....,RATE]

    # Coloco titulo a cada uno
    ax1.set_title('Frecuencia')
    ax2.set_title('Furier')
    # Establezco los limites de cada grafico
    ax1.set_xlim(0, chunk_size)
    ax1.set_ylim(-40000, 40000)

    ax2.set_xlim(20, RATE + 200)
    # La salida de los calculos de furier varian de 0 a 1, meto -1 para verla mejor
    ax2.set_ylim(0, 2)

    line_frecuencia, = ax1.plot(x_frecuencia, np.random.rand(chunk_size), color='r')
    line_furier, = ax2.semilogx(x_furier, np.random.rand(chunk_size), color='b')

    fig2.show()
    for i in db[0]:
        line_frecuencia.set_ydata(i[1])
        line_furier.set_ydata(i[0])

        fig2.canvas.draw()
        fig2.canvas.flush_events()
    print("jijija")


Reproductor()
