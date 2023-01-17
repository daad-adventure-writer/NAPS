NAPS - The New Age PAW-like System - Herramientas para sistemas PAW-like
=========================================================================

Intérprete PAW-like
-------------------

Requisitos:

- Python versión 2.X, ó 3.X superior a 3.2
- Recomendado: PyGame versión 1.X ó 2.X (necesario para que tenga interfaz gráfica)

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
- ``--debug`` (opcional) Ejecuta la base de datos en modo depuración: ejecutando los condactos paso a paso, mientras muestra el valor de las banderas
- ``--gui`` (opcional) Elige la interfaz gráfica a utilizar. Opciones posibles: pygame (interfaz gráfica con PyGame) y stdio (interfaz sólo texto, usando la entrada y salida estándar)
- ``--scale`` (opcional) Elige el factor de escalado de la ventana, de 1 (valor por defecto en modo depuración, sin modo depuración el valor por defecto es 2) a 3, con lo que ampliará todo ese número de veces


Entorno de desarrollo integrado (IDE)
-------------------------------------

Requisitos:

- Python versión 2.X, ó 3.X superior a 3.2
- PyQt versión 4.X ó 5.X

Uso:

``python ide_pyqt.py [base_de_datos] [bd_o_carpeta_gráficos]``

Parámetros:

- ``base_de_datos`` (opcional) Base de datos de Quill/PAWS/SWAN/DAAD a cargar
- ``bd_o_carpeta_gráficos`` (opcional) Base de datos gráfica que usar para las imágenes al depurar, o carpeta de la que tomarlas (con nombre pic###.png)


Instalación de los requisitos en Windows
----------------------------------------

1. Instalar Python 3.X descargando un instalador desde esta web: https://www.python.org/downloads/windows/
2. Abrir el Símbolo del sistema
3. Ejecutar allí estos dos comandos:
   - pip install pygame
   - pip install pyqt5


Agradecimientos
---------------

La siguiente es una lista de personas que han tenido influencia en el desarrollo de estas herramientas, a las cuales estoy agradecido:

- A Ximo por darme motivación, ideas y recomendaciones para que NAPS sea más amigable, para que funcione en Windows también, y sobre todo por desarrollar la integración de NAPS en EAAD bajo DAAD Ready.
- A Uto por su ayuda en numerosas ocasiones investigando las "técnicas secretas" de DAAD, muchas veces a base de pruebas reiteradas e ingeniería inversa. Y por ser ejemplo e inspiración como autor prolífico.
- A dddddd por compartir sus descubrimientos técnicos poco o nada documentados de PAWS, y motivarme para añadir características a NAPS. Fue por él que implementé la interfaz del intérprete para manejarlo por entrada y salida estándar.
- A NatyPC como ejemplo e inspiración con su intérprete para MSX y sus investigaciones del formato de las bases de datos gráficas de DAAD.
- A Joan CiberSheep y Pedro Fernández por reportarme errores detalladamente para poderlos solucionar.
- A los diferentes autores de aventuras conversacionales que me compartieron bases de datos y código fuente para probar e implementar diferentes características en NAPS.

Esta lista desde luego no pretende ser completa, dado que es fácil haber pasado a alguien por alto.
