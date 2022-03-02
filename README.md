NAPS - The New Age PAW-like System - Herramientas para sistemas PAW-like
=========================================================================

Intérprete PAW-like
-------------------

Requisitos:

- Python versión 2.X ó 3.X
- Recomendado para el intérprete: PyGame versión 1.X ó 2.X (necesario para que tenga interfaz gráfica)

Uso:

``python interprete.py [-c|--columns 32..42] [-h|--help] [-D|--debug] [-g|--gui pygame|stdio] [-s|--scale 1|2|3] bd_o_carpeta [bd_o_carpeta_gráficos]``

Ejemplos bajo Windows:
- ``python interprete.py -g stdio -c 42 ..\disappearance\disappearance.sna``
- ``python interprete.py --scale 3 C:\Juegos\templos\amiga``
- ``python interprete.py C:\Juegos\MindFighter\mindf000.adb``

Ejemplos bajos Linux:
- ``python interprete.py -D ../jabato/dos/``
- ``python3 interprete.py --gui pygame ../original/PART2.DDB ../pngs_original_parte2/``
- ``./interprete.py ~/Juegos/Cozumel/amiga ~/Juegos/Cozumel/st/PART1.DAT``

Parámetros:

- ``bd_o_carpeta`` (obligatorio) Base de datos o carpeta de Quill/PAWS/SWAN/DAAD a ejecutar
- ``bd_o_carpeta_gráficos`` (opcional) Base de datos gráfica para las imágenes, o carpeta de la que tomarlas (con nombre pic###.png)
- ``--columns`` (opcional) Cambia el número de columnas a usar cuando se imita la plataforma Spectrum, desde 32 hasta 42 (valor por defecto en interfaz pygame, en la stdio por defecto es sin límite)
- ``--help`` (opcional) Muestra ayuda sobre los parámetros de línea de comandos
- ``--debug`` (opcional) Ejecutar los condactos paso a paso
- ``--gui`` (opcional) Elige la interfaz gráfica a utilizar. Opciones posibles: pygame (interfaz gráfica con PyGame) y stdio (interfaz sólo texto, usando la entrada y salida estándar)
- ``--scale`` (opcional) Elige el factor de escalado de la ventana, de 1 (valor por defecto) a 3, con lo que ampliará todo ese número de veces


Entorno de desarrollo integrado (IDE)
-------------------------------------

Requisitos:

- Python versión 2.X ó 3.X
- Para el IDE: PyQt versión 4.X ó 5.X

Uso:

``python ide_pyqt.py [base_de_datos] [base_de_datos_gráfica]``

Parámetros:

- ``base_de_datos`` (opcional) Base de datos de Quill/PAWS/SWAN/DAAD a cargar
- ``base_de_datos_gráfica`` (opcional) Base de datos gráfica que usar al depurar


Instalación de los requisitos en Windows
----------------------------------------

1. Instalar Python 3.X descargando un instalador desde esta web: https://www.python.org/downloads/windows/
2. Abrir el Símbolo del sistema
3. Ejecutar allí estos dos comandos:
   - pip install pygame
   - pip install pyqt5
