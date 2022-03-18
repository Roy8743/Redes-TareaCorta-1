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
finalizar = False
savedData = []

escuchador = None
seleccion = -1
pausarListener = False

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


def pulsa(tecla):
    global detener
    global iniciar
    global pausa
    if tecla == kb.KeyCode.from_char('i'):
        print("Se ha presionado la tecla iniciar grabacion")
        # Si no esta iniciada, iniciela
        if iniciar == 0:
            iniciar = 1

    # Se presiona el boton de detener grabacion
    elif tecla == kb.KeyCode.from_char('d'):
        print('Se ha presionado la tecla detener')
        if iniciar == 1:
            # pr = 0
            detener = 1

    # Se presiona el boton de pausa/reanudar
    elif tecla == kb.KeyCode.from_char('p'):
        print("Se ha pulsado la tecla reanudar/pausar")
        if iniciar == 1:
            pausa = pausa ^ 1


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


def menuPulsa(tecla):
    if pausarListener:
        return
    if tecla == kb.KeyCode.from_char('1'):
        print("Iniciando analizador")
    elif tecla == kb.KeyCode.from_char('2'):
        print('Iniciando reproductor')
    elif tecla == kb.KeyCode.from_char('3'):
        print("Cerrando programa")


def menuSuelta(tecla):
    global finalizar
    global seleccion
    if pausarListener:
        return
    # Se presiona el boton del analizador
    if tecla == kb.KeyCode.from_char('1'):
        if seleccion < 0:
            seleccion = 0

    # Se presiona el boton del reproductor
    elif tecla == kb.KeyCode.from_char('2'):
        if seleccion < 0:
            seleccion = 1


    # Se presiona el boton de cerrar
    elif tecla == kb.KeyCode.from_char('3'):
        if seleccion < 0:
            seleccion = 2


def Analizador():
    filename = None
    # Crea la interfaz de PyAudio
    p = pa.PyAudio()
    # Esta funcion me toma una senal por medio del microfono y la mete una parte en un chunk

    frames = []  # Esto me ayuda a guardar los cuadros de la grabacion

    dataOrginal = []
    dataFourier = []

    global detener
    global iniciar
    global pausa
    global savedData

    escuchador = kb.Listener(pulsa)
    escuchador.start()

    # Tomo la senal captada por el microfono, tomo un fracmento.
    entradaDeMic = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        output=True,
        frames_per_buffer=chunk_size)

    # Se generan los dos graficos para las ondas de sonido y la transformacion de fourier.
    # Fig es la pantalla donde se encuentran.
    fig, (ax1, ax2) = plt.subplots(2)

    # Se establecen los valores y el espacio para el plano x
    x_frecuencia = np.arange(0, 2 * chunk_size, 2)  # [0,2,4,6,....,2048]
    x_fourier = np.linspace(0, RATE, chunk_size)  # [0,1024,2048,....,RATE]

    # Se coloca titulo a cada grafico
    ax1.set_title('Ondas de Sonido')
    ax2.set_title('Fourier')
    # Se establecen los limites de cada grafico
    ax1.set_xlim(0, chunk_size)
    ax1.set_ylim(-40000, 40000)
    # Se establecen los tamaños de y para ambos planos en los graficos
    ax2.set_xlim(20, RATE + 200)
    ax2.set_ylim(0, 2)

    line_frecuencia, = ax1.plot(x_frecuencia, np.random.rand(chunk_size), color='r')
    # La representacion de frecuencia siempre se hace en graficos semilogaritmicos
    line_fourier, = ax2.semilogx(x_fourier, np.random.rand(chunk_size), color='b')

    fig.show()

    while escuchador.is_alive():

        if pausa:
            # Se detiene la lectura de audio
            entradaDeMic.stop_stream()
            while pausa:
                line_frecuencia.set_ydata(dataOrginal)
                # Se transforma y dibujo el ultimo frame
                line_fourier.set_ydata(np.abs(np.fft.fft(dataOrginal)) * 2 / (11000 * chunk_size))

                fig.canvas.draw()
                fig.canvas.flush_events()
            # Para seguir se renueva el stream
            entradaDeMic = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=True,
                                  frames_per_buffer=chunk_size)
            continue
        # La entrada del audio se lee en 'pedazos'
        data = entradaDeMic.read(chunk_size)

        if iniciar:
            frames.append(data)  # Se guardan los cuadros grabados
        dataOrginal = struct.unpack(str(chunk_size) + 'h', data)
        # Se traducen los bits a datos interpretados dado el formato del parametro 1

        line_frecuencia.set_ydata(dataOrginal)

        # Se realiza una transformacion de fourier sobre la data original para graficarla y guardarla
        temp_ft = np.abs(np.fft.fft(dataOrginal)) * 2 / (11000 * chunk_size)
        if iniciar:
            savedData.append([temp_ft, dataOrginal])
        line_fourier.set_ydata(temp_ft)

        fig.canvas.draw()
        fig.canvas.flush_events()

        if detener:
            # Se detiene el grabado se limpian los eventos y se cierra la ventana
            entradaDeMic.stop_stream()
            entradaDeMic.close()
            escuchador.stop()
            filename = guardar(frames)
            plt.close()
            fig.canvas.flush_events()
            plt.close()
            detener = 0
    return filename


def guardar(frames):
    n = input("Ingrese el nombre del archivo a guardar: ")
    # Se agrega la extensión atm
    filename = n + ".atm"
    dbfile = open(filename, 'ab')

    # Se limpian los datos del archivo si este ya existe
    dbfile.seek(0)
    dbfile.truncate()

    # Se escriben los datos de la grabacion y de los graficos
    db = [savedData, frames]
    pickle.dump(db, dbfile)
    return filename


def playFrames(frames):
    # Crea la interfaz de PyAudio
    p = pa.PyAudio()
    entradaDeMic = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        output=True)

    i = 1
    while i <= (math.ceil(len(frames) / chunk_size)):
        max_i = i * chunk_size
        min_i = (i - 1) * chunk_size
        entradaDeMic.write(b''.join(frames[min_i:max_i]))
        i += 1

    entradaDeMic.stop_stream()
    entradaDeMic.close()
    p.terminate()


def Reproductor(filename):
    print("Reproduciendo")
    # Abre el archivo .atm y carga los datos
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

    # Genera las lineas del grafico
    line_frecuencia, = ax1.plot(x_frecuencia, np.random.rand(chunk_size), color='r')
    line_furier, = ax2.semilogx(x_furier, np.random.rand(chunk_size), color='b')

    fig2.show()

    # Genera un hilo aparte para reproducir el sonido y así coordinar el sonido con los datos del grafico guardados
    hiloPlay = threading.Thread(target=playFrames,
                                args=(db[1],))
    hiloPlay.start()
    # Dibuja el grafico con los datos cargados del archivo
    for i in db[0]:
        line_frecuencia.set_ydata(i[1])
        line_furier.set_ydata(i[0])

        fig2.canvas.draw()
        fig2.canvas.flush_events()
    # Cierra la ventana, por un error de matplot se necesita hacer flush para que el evento de close no se quede en cola
    plt.close()
    fig2.canvas.flush_events()
    plt.close()


def printMenu():
    print("\n\n\nDigite la opción a utilizar:\n" +
          "1 - Analizador\n" +
          "2 - Reproductor\n" +
          "3 - Cerrar\n")


def main():
    global seleccion
    global pausarListener
    while not finalizar:
        # Crea un Listener para las opciones de teclado
        escuchador = kb.Listener(menuPulsa, menuSuelta)
        escuchador.start()
        # Imprime el menu de opciones
        printMenu()

        while escuchador.is_alive():
            # Si la selección fue el Analizador
            if seleccion == 0:
                # Pausa el Listener del menu para no interferir con el las entradas de teclado del Analizador
                pausarListener = True
                Analizador()
                pausarListener = False
                seleccion = -1
                printMenu()
            # Si la selección fue el Reproductor
            if seleccion == 1:
                # Pausa el Listener del menu para no interferir con el las entradas de teclado del Reproductor
                pausarListener = True
                filename = input("Ingrese el nombre del archivo a reproducir(sin .atm):") + ".atm"
                Reproductor(filename)
                pausarListener = False
                seleccion = -1
                printMenu()
            # Si la selección fue salir
            if seleccion == 2:
                # Para el Listener de menu y sale de la aplicación
                escuchador.stop()
                return


main()
# filename = Analizador()
# Reproductor(filename)
