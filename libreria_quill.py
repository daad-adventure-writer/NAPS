# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Librería de QUILL (versión de Spectrum). Parte común a editor, compilador e intérprete
# Copyright (C) 2010, 2018-2020, 2022 José Manuel Ferrer Ortiz
#
# *****************************************************************************
# *                                                                           *
# *  This program is free software; you can redistribute it and/or modify it  *
# *  under the terms of the GNU General Public License version 2, as          *
# *  published by the Free Software Foundation.                               *
# *                                                                           *
# *  This program is distributed in the hope that it will be useful, but      *
# *  WITHOUT ANY WARRANTY; without even the implied warranty of               *
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU         *
# *  General Public License version 2 for more details.                       *
# *                                                                           *
# *  You should have received a copy of the GNU General Public License        *
# *  version 2 along with this program; if not, write to the Free Software    *
# *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA  *
# *                                                                           *
# *****************************************************************************

from bajo_nivel import *
from prn_func   import prn


# Variables que se exportan (fuera del paquete)

# Sólo se usará este módulo de condactos
mods_condactos = ('condactos_quill',)

conexiones     = []   # Listas de conexiones de cada localidad
desc_locs      = []   # Descripciones de las localidades
desc_objs      = []   # Descripciones de los objetos
locs_iniciales = []   # Localidades iniciales de los objetos
msgs_sys       = []   # Mensajes de sistema
msgs_usr       = []   # Mensajes de usuario
nombres_objs   = []   # Palabras de los objetos
num_objetos    = [0]  # Número de objetos (en lista para pasar por referencia)
tablas_proceso = []   # Tablas de proceso (la de estado y la de eventos)
vocabulario    = []   # Vocabulario

max_llevables = 0

# Identificadores (para hacer el código más legible) predefinidos
ids_locs = {  0 : 'INICIAL',
                  'INICIAL'    :   0,
            252 : 'NO_CREADOS',
                  'NO_CREADOS' : 252,
            253 : 'PUESTOS',
                  'PUESTOS'    : 253,
            254 : 'LLEVADOS',
                  'LLEVADOS'   : 254}

# Funciones que importan bases de datos desde ficheros
funcs_exportar = ()  # Ninguna, de momento
funcs_importar = (
  ('carga_bd', ('sna',), 'Imagen de memoria de ZX 48K con Quill'),
)
# Función que crea una nueva base de datos (vacía)
func_nueva = 'nueva_bd'

# Mensajes de sistema predefinidos
nuevos_sys = (
  'Todo está oscuro. No veo nada.',
  'También veo:-',
  '\nEspero tu orden.',
  '\nEstoy listo para recibir instrucciones.',
  '\nDime qué hago.',
  '\nDame tu orden.',
  'Lo siento, no entiendo eso. Intenta otras palabras.',
  'No puedo ir en esa dirección.',
  'No puedo.',
  'Llevo conmigo:-',
  '(puesto)',
  'Nada de nada.',
  '¿Seguro que quieres salir?',
  '\nFIN DEL JUEGO\n¿Quieres volver a probar?',
  'Adiós. Que tengas un buen día.',
  'De acuerdo.',
  'Pulsa cualquier tecla para continuar',
  'He cogido ',
  ' turno',
  's',
  '.',
  'Has completado el ',
  '%',
  'No lo llevo puesto.',
  'No puedo. Mis manos están llenas.',
  'Ya lo tengo.',
  'No está aquí',
  'No puedo cargar más cosas.',
  'No lo tengo.',
  'Ya lo llevo puesto.',
  'S',
  'N'
)


# Constantes que se exportan (fuera del paquete)

INDIRECCION      = False    # El parser no soporta indirección (para el IDE)
LONGITUD_PAL     = 4        # Longitud máxima para las palabras de vocabulario
MAX_LOCS         = 252      # Número máximo de localidades posible
MAX_MSGS_USR     = 255      # Número máximo de mensajes de usuario posible
MAX_PROCS        = 2        # Número máximo de tablas de proceso posible
NUM_ATRIBUTOS    = [0]      # Número de atributos de objeto
NUM_BANDERAS     = 39       # Número de banderas del parser, para compatibilidad. XXX: considerar usar constantes para las banderas del sistema
NUM_BANDERAS_ACC = 33       # Número de banderas del parser accesibles por el programador
NOMBRE_SISTEMA   = 'QUILL'  # Nombre de este sistema
# Nombres de las primeras tablas de proceso (para el IDE)
NOMBRES_PROCS    = ('Tabla de eventos', 'Tabla de estado')
TIPOS_PAL        = ('Palabra',)  # Nombres de los tipos de palabra (para el IDE)


# Diccionarios de condactos

# El formato es el siguiente:
# código : (nombre, lista_parámetros)
# Donde lista_parámetros es una lista con el tipo de cada parámetro
# Y los tipos de los parámetros se definen así:
# 0          : Número de bandera (flagno), de 0 a NUM_BANDERAS_ACC - 1
# 1          : Número de localidad (locno), de 0 a num_localidades - 1
# 2          : Número de mensaje de usuario (mesno), de 0 a num_msgs_usuario - 1
# 3          : Número de mensaje de sistema (sysno), de 0 a num_msgs_sistema - 1
# 4          : Número de objeto (objno), de 0 a num_objetos - 1
# 5          : Número de tabla de proceso (procno), de 0 a num_procesos - 1
# 10-16      : Número de palabra de vocabulario (word), de tipo número - 10,
#              siendo: 0 verbo, 1 adverbio, 2 nombre, 3 adjetivo, 4 preposición,
#              5 conjunción, 6 pronombre
# (mín, máx) : Rango de valores, de mín a máx

# Diccionario de condiciones
condiciones = {
   0 : ('AT',      (      1,         )),
   1 : ('NOTAT',   (      1,         )),
   2 : ('ATGT',    (      1,         )),
   3 : ('ATLT',    (      1,         )),
   4 : ('PRESENT', (      4,         )),
   5 : ('ABSENT',  (      4,         )),
   6 : ('WORN',    (      4,         )),
   7 : ('NOTWORN', (      4,         )),
   8 : ('CARRIED', (      4,         )),
   9 : ('NOTCARR', (      4,         )),
  10 : ('CHANCE',  ((1, 99),         )),  # FIXME: Comprobar si sirven 0 y 100
  11 : ('ZERO',    (      0,         )),
  12 : ('NOTZERO', (      0,         )),
  13 : ('EQ',      (      0, (0, 255))),
  14 : ('GT',      (      0, (0, 255))),
  15 : ('LT',      (      0, (0, 255)))
}

# Diccionario de acciones
acciones = {
   0 : ('INVEN',   ()                  ),
   1 : ('DESC',    ()                  ),
   2 : ('QUIT',    ()                  ),
   3 : ('END',     ()                  ),
   4 : ('DONE',    ()                  ),
   5 : ('OK',      ()                  ),
   6 : ('ANYKEY',  ()                  ),
   7 : ('SAVE',    ()                  ),
   8 : ('LOAD',    ()                  ),
   9 : ('TURNS',   ()                  ),
  10 : ('SCORE',   ()                  ),
  17 : ('PAUSE',   ((0, 255),         )),
  21 : ('GOTO',    (       1,         )),
  22 : ('MESSAGE', (       2,         )),
  23 : ('REMOVE',  (       4,         )),
  24 : ('GET',     (       4,         )),
  25 : ('DROP',    (       4,         )),
  26 : ('WEAR',    (       4,         )),
  27 : ('DESTROY', (       4,         )),
  28 : ('CREATE',  (       4,         )),
  29 : ('SWAP',    (       4,        4)),
  31 : ('SET',     (       0,         )),
  32 : ('CLEAR',   (       0,         )),
  33 : ('PLUS',    (       0, (0, 255))),
  34 : ('MINUS',   (       0, (0, 255))),
  35 : ('LET',     (       0, (0, 255))),
  36 : ('BEEP',    ((0, 255), (0, 255)))
}

# Diccionario de condactos
condactos = {}
for codigo in condiciones:
  condactos[codigo] = condiciones[codigo] + (False,)
for codigo in acciones:
  condactos[100 + codigo] = acciones[codigo] + (True,)


# Funciones que utiliza el IDE o el intérprete directamente

def carga_bd (fichero, longitud):
  """Carga la base de datos entera desde el fichero de entrada

Para compatibilidad con el IDE:
- Recibe como primer parámetro un fichero abierto
- Recibe como segundo parámetro la longitud del fichero abierto
- Devuelve False si ha ocurrido algún error"""
  global fich_ent, fin_cadena, max_llevables, nueva_linea
  # if longitud not in (49179, 131103):  # Tamaño de 48K y de 128K
  if longitud != 49179:
    return False  # No parece un fichero de imagen de memoria de Spectrum
  # Detectamos la posición de la cabecera de la base de datos
  bajo_nivel_cambia_ent (fichero)
  fich_ent = fichero
  posicion = 0
  encajeSec = []
  secuencia = (16, None, 17, None, 18, None, 19, None, 20, None, 21)
  c = carga_int1 (posicion)
  while posicion < longitud:
    if secuencia[len (encajeSec)] == None or c == secuencia[len (encajeSec)]:
      encajeSec.append (c)
      if len (encajeSec) == len (secuencia):
        break
    elif encajeSec:
      del encajeSec[:]
      continue  # Empezamos de nuevo desde este caracter
    c = carga_int1()
    posicion += 1
  else:
    return False  # Cabecera de la base de datos no encontrada
  posicion += 3
  bajo_nivel_cambia_endian (le = True)  # Al menos es así en ZX Spectrum
  bajo_nivel_cambia_despl  (16357)      # Al menos es así en Hampstead, igual que PAWS
  fin_cadena  = 31  # Igual que PAWS
  nueva_linea = 6
  try:
    preparaPosCabecera (posicion)
    cargaCadenas (CAB_NUM_LOCS,     CAB_POS_LST_POS_LOCS,     desc_locs)
    cargaCadenas (CAB_NUM_OBJS,     CAB_POS_LST_POS_OBJS,     desc_objs)
    cargaCadenas (CAB_NUM_MSGS_USR, CAB_POS_LST_POS_MSGS_USR, msgs_usr)
    cargaCadenas (CAB_NUM_MSGS_SYS, CAB_POS_LST_POS_MSGS_SYS, msgs_sys)
    cargaLocalidadesObjetos()
    cargaVocabulario()
    cargaTablasProcesos()
    max_llevables = carga_int1 (CAB_MAX_LLEVABLES)
  except:
    return False

def inicializa_banderas (banderas):
  """Inicializa banderas con valores propios de Quill"""
  # Banderas de sistema, no accesibles directamente, en posición estándar de PAWS
  banderas[37] = max_llevables

def lee_secs_ctrl (cadena):
  """Devuelve la cadena dada convirtiendo las secuencias de control en una representación imprimible"""
  # TODO: el resto de las secuencias de control
  return cadena.replace ('\n', '\\n')

def nueva_bd ():
  """Crea una nueva base de datos de The Quill (versión de Spectrum)"""
  # Creamos la localidad 0
  desc_locs.append  ('Descripción de la localidad 0, la inicial.')
  conexiones.append ([])  # Ninguna conexión en esta localidad
  # Creamos una palabra para el objeto 0
  vocabulario.append(('luz', 13, 0))  # 0 es el tipo de palabra
  # Creamos el objeto 0
  desc_objs.append      ('Descripción del objeto 0, emisor de luz.')
  locs_iniciales.append (ids_locs['NO_CREADOS'])
  nombres_objs.append   (13)
  num_objetos = 1
  # Creamos el mensaje de usuario 0
  msgs_usr.append ('Texto del mensaje 0.')
  # Ponemos los mensajes de sistema predefinidos
  for mensaje in nuevos_sys:
    msgs_sys.append (mensaje)
  # Creamos la tabla de estado y la de eventos
  tablas_proceso.append (([[], []]))
  tablas_proceso.append (([[], []]))


# Funciones auxiliares que sólo se usan en este módulo

def cargaCadenas (posNumCads, posListaPos, cadenas):
  """Carga un conjunto genérico de cadenas

posNumCads es la posición de donde obtener el número de cadenas
posListaPos posición de donde obtener la lista de posiciones de las cadenas
cadenas es la lista donde almacenar las cadenas que se carguen"""
  # Cargamos el número de cadenas
  numCads = carga_int1 (posNumCads)
  # Vamos a la posición de la lista de posiciones de cadenas
  fich_ent.seek (carga_desplazamiento (posListaPos))
  # Cargamos las posiciones de las cadenas
  posiciones = []
  for i in range (numCads):
    posiciones.append (carga_desplazamiento())
  # Cargamos cada cadena
  saltaSiguiente = False  # Si salta el siguiente carácter, como ocurre tras algunos códigos de control
  for posicion in posiciones:
    fich_ent.seek (posicion)
    cadena = []
    while True:
      caracter = carga_int1() ^ 255
      if caracter == fin_cadena:  # Fin de esta cadena
        break
      if saltaSiguiente or (caracter in (range (16, 21))):  # Códigos de control
        cadena.append (chr (caracter))
        saltaSiguiente = not saltaSiguiente
      elif caracter == nueva_linea:  # Un carácter de nueva línea en la cadena
        cadena.append ('\n')
      else:
        cadena.append (chr (caracter))
    cadenas.append (''.join (cadena))

def cargaLocalidadesObjetos ():
  """Carga las localidades iniciales de los objetos (dónde está cada uno)"""
  # Cargamos el número de objetos (no lo tenemos todavía)
  num_objetos[0] = carga_int1 (CAB_NUM_OBJS)
  # Vamos a la posición de las localidades de los objetos
  fich_ent.seek (carga_desplazamiento (CAB_POS_LOCS_OBJS))
  # Cargamos la localidad de cada objeto
  for i in range (num_objetos[0]):
    locs_iniciales.append (carga_int1())

def cargaTablasProcesos ():
  """Carga las dos tablas de procesos: la de estado y la de eventos"""
  # Cargamos cada tabla de procesos
  posiciones = (carga_desplazamiento (CAB_POS_EVENTOS), carga_desplazamiento (CAB_POS_ESTADO))
  for numProceso in range (2):
    posicion = posiciones[numProceso]
    fich_ent.seek (posicion)
    cabeceras   = []
    posEntradas = []
    while True:
      verbo = carga_int1()
      if verbo == 0:  # Fin de este proceso
        break
      cabeceras.append ((verbo, carga_int1()))
      posEntradas.append (carga_desplazamiento())
    entradas = []
    for numEntrada in range (len (posEntradas)):
      posEntrada = posEntradas[numEntrada]
      fich_ent.seek (posEntrada)
      entrada = []
      for listaCondactos in (condiciones, acciones):
        while True:
          numCondacto = carga_int1()
          if numCondacto == 255:  # Fin de esta entrada
            break
          if numCondacto not in listaCondactos:
            prn ('FIXME: Número de', 'condición' if listaCondactos == condiciones else 'acción', numCondacto, 'desconocida, en entrada', numEntrada, 'de la tabla de', 'estado' if numProceso else 'eventos')
          parametros = []
          for i in range (len (listaCondactos[numCondacto][1])):
            parametros.append (carga_int1())
          if listaCondactos == acciones:
            entrada.append ((numCondacto + 100, parametros))
          else:
            entrada.append ((numCondacto, parametros))
      entradas.append (entrada)
    if len (cabeceras) != len (entradas):
      prn ('ERROR: Número distinto de cabeceras y entradas para una tabla de',
           'procesos')
      return
    tablas_proceso.append ((cabeceras, entradas))

def cargaVocabulario ():
  """Carga el vocabulario"""
  # Vamos a la posición del vocabulario
  fich_ent.seek (carga_desplazamiento (CAB_POS_VOCAB))
  # Cargamos cada palabra de vocabulario
  while True:
    caracter = carga_int1()
    if caracter == 0:  # Fin del vocabulario
      return
    caracter ^= 255
    palabra   = [chr (caracter)]
    for i in range (3):
      caracter = carga_int1() ^ 255
      palabra.append (chr (caracter))
    # Quill guarda las palabras de menos de cuatro letras con espacios al final
    # Quill guarda las palabras en mayúsculas
    vocabulario.append ((''.join (palabra).rstrip().lower(), carga_int1(), 0))

def preparaPosCabecera (inicio):
  """Asigna las "constantes" de desplazamientos (offsets/posiciones) en la cabecera"""
  global CAB_MAX_LLEVABLES, CAB_NUM_OBJS, CAB_NUM_LOCS, CAB_NUM_MSGS_USR, CAB_NUM_MSGS_SYS, CAB_POS_EVENTOS, CAB_POS_ESTADO, CAB_POS_LST_POS_OBJS, CAB_POS_LST_POS_LOCS, CAB_POS_LST_POS_MSGS_USR, CAB_POS_LST_POS_MSGS_SYS, CAB_POS_LST_POS_CNXS, CAB_POS_VOCAB, CAB_POS_LOCS_OBJS, CAB_POS_NOMS_OBJS
  CAB_MAX_LLEVABLES        = inicio + 0   # Número máximo de objetos llevables
  CAB_NUM_OBJS             = inicio + 1   # Número de objetos
  CAB_NUM_LOCS             = inicio + 2   # Número de localidades
  CAB_NUM_MSGS_USR         = inicio + 3   # Número de mensajes de usuario
  CAB_NUM_MSGS_SYS         = inicio + 4   # Número de mensajes de sistema
  CAB_POS_EVENTOS          = inicio + 5   # Posición de la tabla de eventos
  CAB_POS_ESTADO           = inicio + 7   # Posición de la tabla de estado
  CAB_POS_LST_POS_OBJS     = inicio + 9   # Posición lista de posiciones de objetos
  CAB_POS_LST_POS_LOCS     = inicio + 11  # Posición lista de posiciones de localidades
  CAB_POS_LST_POS_MSGS_USR = inicio + 13  # Pos. lista de posiciones de mensajes de usuario
  CAB_POS_LST_POS_MSGS_SYS = inicio + 15  # Pos. lista de posiciones de mensajes de usuario
  CAB_POS_LST_POS_CNXS     = inicio + 17  # Posición lista de posiciones de conexiones
  CAB_POS_VOCAB            = inicio + 19  # Posición del vocabulario
  CAB_POS_LOCS_OBJS        = inicio + 21  # Posición de localidades iniciales de objetos
  CAB_POS_NOMS_OBJS        = inicio + 23  # Posición de los nombres de los objetos
