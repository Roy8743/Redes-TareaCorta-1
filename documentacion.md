
# Proyecto Autrum

<b>Estudiantes:</b><br>
Jonder Hernández Gutiérrez - 2018203660<br>
Juan Fernández Hidalgo - 2017100691 <br>
Roy Chavarría Garita - 2018034199 <br>

---

## 1 Instrucciones de instalación

### 1.1 Bibliotecas

Para utilizar correctamente la aplicación Autrum, debe de instalar las siguientes bibliotecas con los siguientes comandos:
<i>
> sudo apt install python3-pip  
> pip3 install PyAudio  
> pip3 install supyr-struct  
> pip3 install matplotlib  
> pip3 install Arrays  
> pip3 install Wave  
> pip3 install threaded  
> pip3 install os-sys  
> pip3 install pynput  
> pip3 install python-time  
> pip3 install pickle5  
</i>

## 2 El programa

### 2.1 Variables globales mas relevantes

1. chunk_size: Esta variable define el tamaño de los trozos del audio en que este será graficado en la aplicación 
2. savedData: Este es un arreglo usado para guardar todos los frames usados para la graficación del audio para su posterior guardado.
3. RATE: Es la frecuencia de muestreo, o sea, el número de muestras por unidad de tiempo.

### 2.2 Módulos

1. Menu: Compuesto por las funciones 'Pulsa','Suelta','MenuPulsa' y 'MenuSuelta' está encargado de cambiar el estado de operación del programa a partir de las entradas dadas por el usuario.

2. Analizador: Compuesto por la función 'Analizador' está encargado de tomar la entrada de audio y graficarla en tiempo real, además de esto debe estar preparado para grabar los frames y el audio de entrada.


3. Guardado de datos: Compuesto por la función 'guardar' está encargado de comprimir y guardar los datos en un archivo con la extensión 'atm', además de anunciar su estado de éxito con la dirección del archivo.

4. Reproductor: Compuesto por la función 'Reproductor' y 'playFrames' se encarga de leer el archivo atm recopilar los datos en este y reproducir el audio y sus frames.

## 3 Como usar el programa

### 3.1 Iniciar programa

Para iniciar el programa se usa el comando:  
```python3 Autrum.py```

### 3.2 Controles

#### 3.2.3 Menu principal

![Menu](img/menu.png "a")  
Como se observa en la imagen anterior, podemos elegir la opción de analizar presionando la tecla número 1, la opción del reproductor con la tecla número 2 o si queremos salir y cerrar el programa, selecionamos la tecla número 3.

#### 3.2.4 Analizador

![Menu](img/analizador.png "a")  
Cuando se está graficando ya sea al momento de analizar o reproducir, podemos interactuar con el programa con las siguientes teclas:

- Tecla i: Inicia la grabación en el modo de Analizador.

- Tecla P: Pausa la grabación o la reproducción.

- Tecla D: Detiene la grabación.

#### 3.2.5 Reproductor
![reproductor](img/reproductor.png "a")  
La anterior imagen muestra un espacio para poder ingresar el nombre del archivo Autrum, se pide el nombre para cargar y reproducir un archivo Autrum anteriormente creado.

![reproduccion](img/reproducir.png "a")  
En la anterior imagen se puede ver como se reproduce el audio previamente guardado.

![guardado](img/guardado.png "a")  
La anterior imagen muestra un espacio para poder ingresar el nombre del archivo Autrum, se pide el nombre para guardar un archivo en formato Autrum.

# Referencias:

1. Farhan, M., 2020. Latest Spectrum Analyser Using Python | Part-2. Deep Focus. Disponible en: [https://fazals.ddns.net/spectrum-analyser-part-2](https://fazals.ddns.net/spectrum-analyser-part-2)
2. De Langen, J., 2020. Playing and Recording Sound in Python – Real Python. Realpython.com. Disponible en: [https://realpython.com/playing-and-recording-sound-python](https://realpython.com/playing-and-recording-sound-python)
3. Código Pitón. 2022. Cómo Detectar la Pulsación de una Tecla en Python - Código Pitón. Disponible en: [https://www.codigopiton.com/detectar-pulsacion-de-tecla-en-python](https://www.codigopiton.com/detectar-pulsacion-de-tecla-en-python) 