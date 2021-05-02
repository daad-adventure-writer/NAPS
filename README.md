NAPS - The New Age PAW-like System - Herramientas para sistemas PAW-like
=========================================================================

Intérprete PAW-like
-------------------

Requisitos:

- Python versión 2.X ó 3.X
- Recomendado para el intérprete: PyGame versión 1.X ó 2.X (necesario para que tenga interfaz gráfica)

Pasos previos:

- Enlazar, renombrar o copiar el fichero de la interfaz deseada dejándola con el nombre `gui.py`
  - Se puede elegir entre las siguientes:
    - Interfaz gráfica PyGame: `gui_pygame.py`
    - Interfaz sólo texto, usando la entrada y salida estándar: `gui_stdio.py`

Uso:

``interprete.py [-h|--help] [-D|--debug] base_de_datos [carpeta_gráficos]``

Parámetros:

- ``base_de_datos`` (obligatorio) Base de datos de PAWS/SWAN/DAAD a ejecutar
- ``carpeta_gráficos`` (opcional) Carpeta que contiene las imágenes (con nombre pic###.png)
- ``--help`` (opcional) Muestra ayuda sobre los parámetros de línea de comandos
- ``--debug`` (opcional) Ejecutar los condactos paso a paso


Entorno de desarrollo integrado (IDE)
-------------------------------------

Requisitos:

- Python versión 2.X ó 3.X
- Para el IDE: PyQt versión 4

Uso:

``ide_pyqt4.py [base_de_datos]``

Parámetros:

- ``base_de_datos`` (opcional) Base de datos de PAWS/SWAN/DAAD a cargar