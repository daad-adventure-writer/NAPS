NAPS - The New Age PAW-like System - Herramientas para sistemas PAW-like
=========================================================================

Intérprete PAW-like
-------------------

![Intérprete de NAPS ejecutando "La Maldición de Rabenstein" (sistema DAAD, plataforma PC, con gráficos VGA)](Intérprete_NAPS_-_Ejecutando_DAAD.png "Intérprete de NAPS ejecutando 'La Maldición de Rabenstein' (sistema DAAD, plataforma PC, con gráficos VGA)")

![Intérprete de NAPS depurando "Las Aventuras de Rudolphine Rur" (sistema DAAD, plataforma PC, con gráficos VGA)](Intérprete_NAPS_-_Depurando_DAAD.png "Intérprete de NAPS depurando 'Las Aventuras de Rudolphine Rur' (sistema DAAD, plataforma PC, con gráficos VGA)")

Requisitos:

- Python versión 2.X superior a 2.5, ó 3.X superior a 3.2
- Recomendado: PyGame versión 1.X ó 2.X (necesario para que tenga interfaz gráfica)
- Opcional: Lark versión 0.X para Python 2.X, o cualquiera para Python 3.X (necesario para importar código fuente SCE)

Uso:

``python interprete.py [-h|--help] [-c|--columns 32..42] [--conversion módulo] [-D|--debug] [-g|--gui pygame|stdio|telegram] [-s|--scale 1..9] bd_cf_o_carpeta [bd_o_carpeta_gráficos]``

Ejemplos bajo Windows:
- ``python interprete.py -g stdio -c 42 ..\disappearance\disappearance.sna``
- ``python interprete.py --scale 3 C:\Juegos\templos\amiga``
- ``python interprete.py C:\Juegos\MindFighter\mindf000.adb``

Ejemplos bajos Linux:
- ``python interprete.py -D ../jabato/dos/``
- ``python3 interprete.py --gui pygame ../original/PART2.DDB ../pngs_original_parte2/``
- ``./interprete.py ~/Juegos/Cozumel/amiga ~/Juegos/Cozumel/st/PART1.DAT``
- ``naps/interprete.py proyecto/misterioso.sce -s3``
- ``./interprete.py -g telegram juegos/firfurcio/firfurcio.sna --conversion conv/firfurcio.py``

Parámetros:

- ``bd_cf_o_carpeta`` (obligatorio) Base de datos, código fuente SCE o carpeta de Quill/PAWS/SWAN/DAAD a ejecutar
- ``bd_o_carpeta_gráficos`` (opcional) Base de datos gráfica para las imágenes, o carpeta de la que tomarlas (con nombre pic###.png)
- ``--help`` (opcional) Muestra ayuda sobre los parámetros de línea de comandos
- ``--columns`` (opcional) Cambia el número de columnas a usar cuando se imita la plataforma Spectrum, desde 32 hasta 42 (valor por defecto en interfaz pygame, en la stdio por defecto es sin límite)
- ``--conversion`` (opcional) Actualiza el diccionario de conversión de caracteres (usado al cargar bases de datos de PAWS para Spectrum) con los valores del diccionario conversion del fichero de módulo Python dado, y el de conversión de secuencias de caracteres (usado en la interfaz de Telegram) con los valores del diccionario secuencias de dicho módulo
- ``--debug`` (opcional) Ejecuta la base de datos en modo depuración: ejecutando los condactos paso a paso, mientras muestra el valor de las banderas
- ``--gui`` (opcional) Elige la interfaz gráfica a utilizar. Opciones posibles: pygame (interfaz gráfica con PyGame), stdio (interfaz sólo texto, usando la entrada y salida estándar) y telegram (interfaz para el bot de Telegram)
- ``--scale`` (opcional) Elige el factor de escalado de la ventana, desde 1 hasta 9, con lo que ampliará todo hasta ese número de veces sin superar la resolución de pantalla. El valor por defecto será el factor máximo dentro de la resolución de pantalla


Entorno de desarrollo integrado (IDE)
-------------------------------------

![IDE de NAPS depurando "La Diosa de Cozumel" (sistema DAAD, plataforma PC, con gráficos CGA)](IDE_NAPS_-_Depurador_de_DAAD.png "IDE de NAPS depurando 'La Diosa de Cozumel' (sistema DAAD, plataforma PC, con gráficos CGA)")

Requisitos:

- Python versión 2.X superior a 2.5, ó 3.X superior a 3.2
- PyQt versión 4.X ó 5.X
- Opcional: Lark versión 0.X para Python 2.X, o cualquiera para Python 3.X (necesario para importar código fuente SCE)

Uso:

``python ide_pyqt.py [-h|--help] [-ne|--no-entry-end] [-r|--run] [bd_o_codigo] [bd_o_carpeta_gráficos]``

Parámetros:

- ``bd_o_codigo`` (opcional) Base de datos o código fuente SCE de Quill/PAWS/SWAN/DAAD a cargar
- ``bd_o_carpeta_gráficos`` (opcional) Base de datos gráfica que usar para las imágenes al depurar, o carpeta de la que tomarlas (con nombre pic###.png)
- ``--help`` (opcional) Muestra ayuda sobre los parámetros de línea de comandos
- ``--no-entry-end`` (opcional) Omite en entradas de proceso los condactos que haya detrás de los que cambian el flujo de ejecución incondicionalmente (como DONE), muy útil para bases de datos compiladas con DRC sin activar el modo clásico, donde no pone marcas de fin de entrada cuando hay algún condacto así, y descarta los condactos que haya después
- ``--run`` (opcional) Ejecuta la base de datos pasada como parámetro directamente, depurando por pasos


Instalación de los requisitos en Windows
----------------------------------------

1. Instalar Python 3.X descargando un instalador desde esta web: https://www.python.org/downloads/windows/
2. Abrir el Símbolo del sistema
3. Ejecutar allí estos comandos:
   - pip install pygame
   - pip install pyqt5
   - pip install lark


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
