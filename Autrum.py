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

iniciar = 0
detener = 0
pau = 0


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
    global pau

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
        if iniciar == 1 and pau == 1:
            # pr = 0
            detener = 1

        elif iniciar == 1 and pau == 0:
            detener = 1

    # Se presiona el boton de pausa/reanudar
    elif tecla == kb.KeyCode.from_char('p'):
        if iniciar == 1:
            if pau == 0:
                pau = 1
            elif pau == 1:
                pau = 0


# Numero de fotogramas en la cual se dividen las senales
CHUNK = 2048  # tomo 2048 y proceso, luego tomo otros 2048 y asi sucesivamente

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


def Analizador():
    # Esta funcion me toma una senal por medio del microfono y la mete una parte en un chunk

    frames = []  # Esto me ayuda a guardar los cuadros de la grabacion

    global detener
    global iniciar
    global pau

    escuchador = kb.Listener(pulsa, suelta)
    escuchador.start()
    # escuchador.join()

    # Tomo la senal captada por el microfono, tomo un fracmento.
    toma = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        output=True,
        frames_per_buffer=CHUNK)

    # Basicamente son dos graficos diferentes, el 2 significa 2 filas. Fig es la pantalla donde se encuentran.
    fig, (ax1, ax2) = plt.subplots(2)

    # Me devuelve una lista dentro de un intervalo
    x_frecuencia = np.arange(0, 2 * CHUNK, 2)  # [0,2,4,6,....,2048]
    x_furier = np.linspace(0, RATE, CHUNK)  # [0,1024,2048,....,RATE]

    # Coloco titulo a cada uno
    ax1.set_title('Frecuencia')
    ax2.set_title('Furier')

    # Establezco los limites de cada grafico
    ax1.set_xlim(0, CHUNK)
    ax1.set_ylim(-40000, 40000)

    ax2.set_xlim(20, RATE)
    # La salida de los calculos de furier varian de 0 a 1, meto -1 para verla mejor
    ax2.set_ylim(-1, 1)

    line_frecuencia, = ax1.plot(x_frecuencia, np.random.rand(CHUNK), 'r')
    # La representacion de frecuencia siempre se hace en graficos semilogaritmicos
    line_furier, = ax2.semilogx(x_furier, np.random.rand(CHUNK), 'b')

    fig.show()

    # Pa
    dataInt2 = []

    savedData = []

    while escuchador.is_alive():

        if pau == 1:
            # Tengo que dejar de tomar el stream, lo cierro de una
            toma.stop_stream()
            while pau:
                line_frecuencia.set_ydata(dataInt2)
                # aca trasnformamos la senal con furier
                line_furier.set_ydata(np.abs(np.fft.fft(dataInt)) * 2 / (11000 * CHUNK))

                fig.canvas.draw()
                fig.canvas.flush_events()
            # vuelvo a abrir el stram
            toma = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=True, frames_per_buffer=CHUNK)
            continue

        data = toma.read(CHUNK)

        if pau == 0 and iniciar == 1:
            frames.append(data)  # Guardo o grabo los cuadros
        dataInt = struct.unpack(str(CHUNK) + 'h', data)  # ESto lo hago mas que todo para graficar

        line_frecuencia.set_ydata(dataInt)
        # aca trasnformamos la senal con furier
        temp_fft = np.abs(np.fft.fft(dataInt)) * 2 / (11000 * CHUNK)
        savedData.append([temp_fft,dataInt])
        line_furier.set_ydata(temp_fft)

        fig.canvas.draw()
        fig.canvas.flush_events()

        if detener == 1:
            toma.stop_stream()
            toma.close()
            p.terminate()
            escuchador.stop()
            guardarGrabacion(frames)

        dataInt2 = dataInt
    
    for i in savedData:
        line_frecuencia.set_ydata(i[1])
        line_furier.set_ydata(i[0])

        fig.canvas.draw()
        fig.canvas.flush_events()


def guardarGrabacion(frames):
    # Guardo el audio grabado
    # os.system("clear")
    n = input("Ingrese el nombre del archivo a guardar: ")
    n = n + '.wav'
    gb = wave.open(n, 'wb')
    gb.setnchannels(CHANNELS)
    gb.setsampwidth(p.get_sample_size(FORMAT))
    gb.setframerate(RATE)
    gb.writeframes(b''.join(frames))
    gb.close()


Analizador()


def Reproductor():
    print("jiji")


Reproductor()
