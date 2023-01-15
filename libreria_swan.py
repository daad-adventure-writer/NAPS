# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Librería de SWAN (parte común a editor, compilador e intérprete)
# Copyright (C) 2020-2023 José Manuel Ferrer Ortiz
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

# Ponemos los módulos de condactos en orden, para permitir que las funciones de los condactos de igual firma (nombre, tipo y número de parámetros) de los sistemas más nuevos tengan precedencia sobre las de sistemas anteriores
mods_condactos = ('condactos_swan', 'condactos_paws', 'condactos_quill')

atributos      = []   # Atributos de los objetos
conexiones     = []   # Listas de conexiones de cada localidad
desc_locs      = []   # Descripciones de las localidades
desc_objs      = []   # Descripciones de los objetos
locs_iniciales = []   # Localidades iniciales de los objetos
msgs_sys       = []   # Mensajes de sistema
msgs_usr       = []   # Mensajes de usuario
nombres_objs   = []   # Nombre y adjetivo de los objetos
num_objetos    = [0]  # Número de objetos (en lista para pasar por referencia)
tablas_proceso = []   # Tablas de proceso
vocabulario    = []   # Vocabulario

# Funciones que importan bases de datos desde ficheros
funcs_exportar = ()  # Ninguna, de momento
funcs_importar = (('carga_bd', ('adb',), 'Bases de datos SWAN'), )
# Función que crea una nueva base de datos (vacía)
func_nueva = ''


# Constantes que se exportan (fuera del paquete)

INDIRECCION      = False    # El parser no soporta indirección (para el IDE)
LONGITUD_PAL     = 5        # Longitud máxima para las palabras de vocabulario
NOMBRE_SISTEMA   = 'SWAN'   # Nombre de este sistema
NUM_ATRIBUTOS    = [8]      # Número de atributos de objeto
NUM_BANDERAS     = 256      # Número de banderas del parser
# Nombres de las primeras tablas de proceso (para el IDE)
NOMBRES_PROCS    = ('Tabla de respuestas', 'Tras la descripción', 'Cada turno')
# Nombres de los tipos de palabra (para el IDE)
TIPOS_PAL = ('Verbo', 'Adverbio', 'Nombre', 'Adjetivo', 'Preposicion', 'Conjuncion', 'Pronombre')


# Desplazamientos (offsets/posiciones) en la cabecera
CAB_PLATAFORMA            =  0  # Identificador de plataforma
CAB_NUM_OBJS              =  4  # Número de objetos
CAB_NUM_LOCS              =  5  # Número de localidades
CAB_NUM_MSGS_USR          =  6  # Número de mensajes de usuario
CAB_NUM_MSGS_SYS          =  7  # Número de mensajes de sistema
CAB_NUM_PROCS             =  8  # Número de procesos
CAB_POS_ABREVS            =  9  # Posición de las abreviaturas
CAB_POS_LST_POS_PROCS     = 11  # Posición lista de posiciones de procesos
CAB_POS_LST_POS_OBJS      = 13  # Posición lista de posiciones de objetos
CAB_POS_LST_POS_LOCS      = 15  # Posición lista de posiciones de localidades
CAB_POS_LST_POS_MSGS_USR  = 17  # Pos. lista de posiciones de mensajes de usuario
CAB_POS_LST_POS_MSGS_SYS  = 19  # Pos. lista de posiciones de mensajes de sistema
CAB_POS_LST_POS_CNXS      = 21  # Posición lista de posiciones de conexiones
CAB_POS_VOCAB             = 23  # Posición del vocabulario
CAB_POS_LOCS_OBJS         = 25  # Posición de localidades iniciales de objetos
CAB_POS_NOMS_OBJS         = 27  # Posición de los nombres de los objetos
CAB_POS_ATRIBS_OBJS       = 29  # Posición de los atributos de los objetos
CAB_LONG_FICH             = 31  # Longitud de la base de datos

alinear        = False  # Si alineamos con relleno (padding) las listas de desplazamientos a posiciones pares
compatibilidad = True   # Modo de compatibilidad con los intérpretes originales
despl_ini      = 0      # Desplazamiento inicial para cargar desde memoria

# Desplazamientos iniciales para cargar desde memoria, de las plataformas en las que éste no es 0
despl_ini_plat = {
  2561: (19072, 38400),  # Commodore 64, Spectrum 48K
  2817: 10240,  # Amstrad CPC
}
plats_word = (266, )  # Plataformas que no pueden leer words en desplazamientos impares (Amiga/PC)


# Diccionario de condactos

condactos = {
  # El formato es el siguiente:
  # código : (nombre, parámetros, es_acción, flujo)
  # Donde:
  #   parámetros es una cadena con el tipo de cada parámetro
  #   flujo indica si el condacto cambia el flujo de ejecución incondicionalmente, por lo que todo código posterior en su entrada será inalcanzable
  # Y los tipos de los parámetros se definen así:
  # % : Porcentaje (percent), de 1 a 99 (TODO: comprobar si sirven 0 y 100)
  # b : Número de bit, de 0 a 7
  # f : Número de bandera (flagno), de 0 a NUM_BANDERAS - 1
  # j : Número de palabra de tipo adjetivo (adjective), ó 255
  # l : Número de localidad (locno), de 0 a num_localidades - 1
  # L : Número de localidad (locno+), de 0 a num_localidades - 1, ó 252-255
  # m : Número de mensaje de usuario (mesno), de 0 a num_msgs_usuario - 1
  # n : Número de palabra de tipo nombre (noun), ó 255
  # o : Número de objeto (objno), de 0 a num_objetos - 1
  # p : Número de process (procno), de 0 a num_procesos - 1
  # r : Número de palabra de tipo preposición (preposition), ó 255
  # s : Número de mensaje de sistema (sysno), de 0 a num_msgs_sistema - 1
  # u : Valor (value) entero sin signo, de 0 a 255
  # v : Número de palabra de tipo adverbio (adverb), ó 255
    0 : ('AT',      'l',  False, False),
    1 : ('NOTAT',   'l',  False, False),
    2 : ('ATGT',    'l',  False, False),
    3 : ('ATLT',    'l',  False, False),
    4 : ('PRESENT', 'o',  False, False),
    5 : ('ABSENT',  'o',  False, False),
    6 : ('WORN',    'o',  False, False),
    7 : ('NOTWORN', 'o',  False, False),
    8 : ('CARRIED', 'o',  False, False),
    9 : ('NOTCARR', 'o',  False, False),
   10 : ('CHANCE',  '%',  False, False),
   11 : ('ZERO',    'f',  False, False),
   12 : ('NOTZERO', 'f',  False, False),
   13 : ('EQ',      'fu', False, False),
   14 : ('GT',      'fu', False, False),
   15 : ('LT',      'fu', False, False),
   16 : ('ADJECT1', 'j',  False, False),
   17 : ('ADVERB',  'v',  False, False),
   # 18 : ('_18_',    '',   True,  True),   # Formerly INVEN
   19 : ('DESC',    '',   True,  True),
   20 : ('QUIT',    '',   False, False),  # Se comporta como condición, no satisfecha si no termina
   21 : ('END',     '',   True,  True),
   22 : ('DONE',    '',   True,  True),
   23 : ('OK',      '',   True,  True),
   24 : ('ANYKEY',  '',   True,  False),
   25 : ('SAVE',    '',   True,  True),
   26 : ('LOAD',    '',   True,  True),
   27 : ('TURNS',   '',   True,  False),
   28 : ('SCORE',   '',   True,  False),
   # 29 : ('_29_',    '',   True,  False),  # Formerly CLS
   30 : ('DROPALL', '',   True,  False),
   31 : ('AUTOG',   '',   True,  False),
   32 : ('AUTOD',   '',   True,  False),
   33 : ('AUTOW',   '',   True,  False),
   34 : ('AUTOR',   '',   True,  False),
   35 : ('PAUSE',   'u',  True,  False),
   36 : ('TIMEOUT', '',   False, False),
   37 : ('GOTO',    'l',  True,  False),
   38 : ('MESSAGE', 'm',  True,  False),
   39 : ('REMOVE',  'o',  True,  False),
   40 : ('GET',     'o',  True,  False),
   41 : ('DROP',    'o',  True,  False),
   42 : ('WEAR',    'o',  True,  False),
   43 : ('DESTROY', 'o',  True,  False),
   44 : ('CREATE',  'o',  True,  False),
   45 : ('SWAP',    'oo', True,  False),
   46 : ('PLACE',   'oL', True,  False),  # TODO: investigar más si en algún caso se comporta como condición
   47 : ('SET',     'f',  True,  False),
   48 : ('CLEAR',   'f',  True,  False),
   49 : ('PLUS',    'fu', True,  False),
   50 : ('MINUS',   'fu', True,  False),
   51 : ('LET',     'fu', True,  False),
   52 : ('NEWLINE', '',   True,  False),
   53 : ('PRINT',   'f',  True,  False),
   54 : ('SYSMESS', 's',  True,  False),
   55 : ('ISAT',    'oL', False, False),
   56 : ('COPYOF',  'of', True,  False),
   57 : ('COPYOO',  'oo', True,  False),
   58 : ('COPYFO',  'fo', True,  False),
   59 : ('COPYFF',  'ff', True,  False),
   60 : ('LISTOBJ', '',   True,  False),
   # 61 : ('_61_',    '',   True,  False),   # Formerly EXTERN
   62 : ('RAMSAVE', '',   True,  False),
   63 : ('RAMLOAD', 'f',  True,  False),
   # 64 : ('_64_',    '',   True,  False),   # Formerly BEEP/BELL
   # 65 : ('_65_',    '',   True,  False),   # Formerly PAPER
   # 66 : ('_66_',    '',   True,  False),   # Formerly INK
   # 67 : ('_67_',    '',   True,  False),   # Formerly BORDER
   68 : ('PREP',    'r',  False, False),
   69 : ('NOUN2',   'n',  False, False),
   70 : ('ADJECT2', 'j',  False, False),
   71 : ('ADD',     'ff', True,  False),
   72 : ('SUB',     'ff', True,  False),
   73 : ('PARSE',   '',   False, False),  # Se comporta como condición, satisfecha con frase inválida
   74 : ('LISTAT',  'L',  True,  False),
   75 : ('PROCESS', 'p',  True,  False),
   76 : ('SAME',    'ff', False, False),
   77 : ('MES',     'm',  True,  False),
   # 78 : ('_78_',    '',   True,  False),   # Formerly CHARSET
   79 : ('NOTEQ',   'fu', False, False),
   80 : ('NOTSAME', 'ff', False, False),
   # 81 : ('_81_',    '',   True,  False),   # Formerly MODE
   # 82 : ('_82_',    '',   True,  False),   # Formerly LINE
   # 83 : ('_83_',    '',   True,  False),   # Formerly TIME
   # 84 : ('_84_',    '',   True,  False),   # Formerly PICTURE
   85 : ('DOALL',   'L',  True,  False),
   # 86 : ('_86_',    '',   True,  False),   # Formerly PROMPT
   # 87 : ('_87_',    '',   True,  False),   # Formerly GRAPHIC
   88 : ('ISNOTAT', 'oL', False, False),
   89 : ('WEIGH',   'of', True,  False),
   90 : ('PUTIN',   'ol', True,  False),
   91 : ('TAKEOUT', 'ol', True,  False),
   92 : ('NEWTEXT', '',   True,  False),
   # 93 : ('_93_',    '',   True,  False),   # Formerly ABILITY
   94 : ('WEIGHT',  'f',  True,  False),
   95 : ('RANDOM',  'f',  True,  False),
   # 96 : ('_96_',    '',   True,  False),   # Formerly INPUT
   # 97 : ('_97_',    '',   True,  False),   # Formerly SAVEAT
   # 98 : ('_98_',    '',   True,  False),   # Formerly BACKAT
   # 99 : ('_99_',    '',   True,  False),   # Formerly PRINTAT
  100 : ('WHATO',   '',   True,  False),
  # 101 : ('_101_',   '',   True,  False),   # Formerly RESET
  102 : ('PUTO',    'L',  True,  False),
  103 : ('NOTDONE', '',   True,  True),
  104 : ('AUTOP',   'l',  True,  False),
  105 : ('AUTOT',   'l',  True,  False),
  106 : ('MOVE',    'f',  False, False),  # Se comporta como condición
  # 107 : ('_107_',   '',   True,  False),   # Formerly PROTECT
  # Desde aquí, todos estos son nuevos en SWAN
  108 : ('OAT',     'of', False, False),
  109 : ('FGET',    'ff', True,  False),
  110 : ('FPUT',    'ff', True,  False),
  111 : ('FMES',    'f',  True,  False),
  112 : ('SETB',    'fb', True,  False),
  113 : ('CLEARB',  'fb', True,  False),
  114 : ('BSET',    'fb', False, False),
  115 : ('NOTBSET', 'fb', False, False),
  116 : ('NOTOAT',  'of', False, False),
  117 : ('OOPSAVE', '',   True,  False),
  118 : ('OOPS',    'f',  True,  False),
  119 : ('GON',     '',   True,  False),
  120 : ('GOFF',    '',   True,  False),
  121 : ('OVERLAY', 'u',  True,  False),
  122 : ('COMMAND', '',   True,  False),
  123 : ('CSAVE',   '',   True,  False),
  124 : ('CLOAD',   '',   True,  False),
}


# Funciones que utiliza el IDE o el intérprete directamente

def cadena_es_mayor (cadena1, cadena2):
  """Devuelve si la cadena1 es mayor a la cadena2 en el juego de caracteres de este sistema"""
  return cadena1 > cadena2

# Carga la base de datos entera desde el fichero de entrada
# Para compatibilidad con el IDE:
# - Recibe como primer parámetro un fichero abierto
# - Recibe como segundo parámetro la longitud del fichero abierto
# - Devuelve False si ha ocurrido algún error
def carga_bd (fichero, longitud):
  global fich_ent, long_fich_ent  # Fichero de entrada y su longitud
  fich_ent      = fichero
  long_fich_ent = longitud
  bajo_nivel_cambia_ent (fichero)
  try:
    preparaPlataforma()
    cargaAbreviaturas()
    cargaCadenas (CAB_NUM_LOCS,     CAB_POS_LST_POS_LOCS,     desc_locs)
    cargaCadenas (CAB_NUM_OBJS,     CAB_POS_LST_POS_OBJS,     desc_objs)
    cargaCadenas (CAB_NUM_MSGS_USR, CAB_POS_LST_POS_MSGS_USR, msgs_usr)
    cargaCadenas (CAB_NUM_MSGS_SYS, CAB_POS_LST_POS_MSGS_SYS, msgs_sys)
    cargaAtributos()
    cargaConexiones()
    cargaLocalidadesObjetos()
    cargaVocabulario()
    cargaNombresObjetos()
    cargaTablasProcesos()
  except:
    return False

def escribe_secs_ctrl (cadena):
  """Devuelve la cadena dada convirtiendo la representación de secuencias de control en sus códigos"""
  # TODO: implementar
  return cadena

def lee_secs_ctrl (cadena):
  """Devuelve la cadena dada convirtiendo las secuencias de control en una representación imprimible"""
  return cadena.replace ('\\', '\\\\').replace ('\n', '\\n')


# Funciones de apoyo de alto nivel

# Carga las abreviaturas
def cargaAbreviaturas ():
  global abreviaturas
  abreviaturas = []
  # Vamos a la posición de las abreviaturas
  posicion = carga_desplazamiento (CAB_POS_ABREVS)
  if posicion == 0:  # Sin abreviaturas
    return
  fich_ent.seek (posicion)
  for i in range (129):
    abreviatura = []
    seguir      = True
    while seguir:
      caracter = carga_int1()
      if caracter > 127:
        caracter -= 128
        seguir    = False
      abreviatura.append (chr (caracter))
    abreviaturas.append (''.join (abreviatura))
    #prn (i, ' |', abreviaturas[-1], '|', sep = '')

# Carga los atributos de los objetos
def cargaAtributos ():
  # Cargamos el número de objetos (no lo tenemos todavía)
  fich_ent.seek (CAB_NUM_OBJS)
  num_objetos[0] = carga_int1()
  # Vamos a la posición de los atributos de los objetos
  fich_ent.seek (carga_desplazamiento (CAB_POS_ATRIBS_OBJS))
  # Cargamos los atributos de cada objeto
  for i in range (num_objetos[0]):
    atributos.append (carga_int1())

# Carga un conjunto genérico de cadenas
# pos_num_cads es la posición de donde obtener el número de cadenas
# pos_lista_pos posición de donde obtener la lista de posiciones de las cadenas
# cadenas es la lista donde almacenar las cadenas que se carguen
def cargaCadenas (pos_num_cads, pos_lista_pos, cadenas):
  # Cargamos el número de cadenas
  fich_ent.seek (pos_num_cads)
  num_cads = carga_int1()
  # Vamos a la posición de la lista de posiciones de cadenas
  fich_ent.seek (carga_desplazamiento (pos_lista_pos))
  # Cargamos las posiciones de las cadenas
  posiciones = []
  for i in range (num_cads):
    posiciones.append (carga_desplazamiento())
  # Cargamos cada cadena
  for posicion in posiciones:
    fich_ent.seek (posicion)
    cadena = []
    while True:
      caracter = carga_int1() ^ 255
      if caracter == ord ('\n'):  # Fin de esta cadena
        break
      if (caracter >= 127) and abreviaturas:
        try:
          cadena.append (abreviaturas[caracter - 127])
        except:
          prn (caracter)
          raise
        # Parece que hay 129 abreviaturas (si no son más), en lugar de 128
        # TODO: comprobar en DAAD primera y última abreviatura, y último
        # caracter no abreviado permitido
      elif caracter == ord ('\r'):  # Un carácter de nueva línea en la cadena
        cadena.append ('\n')
      else:
        cadena.append (chr (caracter))
    cadenas.append (''.join (cadena))

# Carga las conexiones
def cargaConexiones ():
  # Cargamos el número de localidades
  fich_ent.seek (CAB_NUM_LOCS)
  num_locs = carga_int1()
  # Vamos a la posición de la lista de posiciones de las conexiones
  fich_ent.seek (carga_desplazamiento (CAB_POS_LST_POS_CNXS))
  # Cargamos las posiciones de las conexiones de cada localidad
  posiciones = []
  for i in range (num_locs):
    posiciones.append (carga_desplazamiento())
  # Cargamos las conexiones de cada localidad
  for posicion in posiciones:
    fich_ent.seek (posicion)
    salidas = []
    while True:
      verbo = carga_int1()  # Verbo de dirección
      if verbo == 255:  # Fin de las conexiones de esta localidad
        break
      destino = carga_int1()  # Localidad de destino
      salidas.append ((verbo, destino))
    conexiones.append (salidas)

def cargaLocalidadesObjetos ():
  """Carga las localidades iniciales de los objetos (dónde está cada uno)"""
  # Vamos a la posición de las localidades de los objetos
  fich_ent.seek (carga_desplazamiento (CAB_POS_LOCS_OBJS))
  # Cargamos la localidad de cada objeto
  for i in range (num_objetos[0]):
    locs_iniciales.append (carga_int1())

def cargaNombresObjetos ():
  """Carga los nombres y adjetivos de los objetos"""
  # Vamos a la posición de los nombres de los objetos
  fich_ent.seek (carga_desplazamiento (CAB_POS_NOMS_OBJS))
  # Cargamos el nombre y adjetivo de cada objeto
  for i in range (num_objetos[0]):
    nombres_objs.append ((carga_int1(), carga_int1()))

# Carga las tablas de procesos
# El proceso 0 es la tabla de respuestas
# En los procesos 1 y 2, las cabeceras de las entradas se ignoran
def cargaTablasProcesos ():
  # Cargamos el número de procesos
  fich_ent.seek (CAB_NUM_PROCS)
  num_procs = carga_int1()
  # prn (num_procs, 'procesos')
  # Vamos a la posición de la lista de posiciones de los procesos
  fich_ent.seek (carga_desplazamiento (CAB_POS_LST_POS_PROCS))
  # Cargamos las posiciones de los procesos
  posiciones = []
  for i in range (num_procs):
    posiciones.append (carga_desplazamiento())
  # Cargamos cada tabla de procesos
  for num_proceso in range (num_procs):
    posicion = posiciones[num_proceso]
    fich_ent.seek (posicion)
    cabeceras    = []
    pos_entradas = []
    while True:
      verbo = carga_int1()
      if verbo == 0:  # Fin de este proceso
        break
      cabeceras.append ((verbo, carga_int1()))
      pos_entradas.append (carga_desplazamiento())
    entradas = []
    for num_entrada in range (len (pos_entradas)):
      pos_entrada = pos_entradas[num_entrada]
      fich_ent.seek (pos_entrada)
      entrada = []
      while True:
        condacto = carga_int1()
        if condacto == 255:  # Fin de esta entrada
          break
        if condacto > 127:  # Condacto con indirección
          num_condacto = condacto - 128
        else:
          num_condacto = condacto
        parametros = []
        if num_condacto not in condactos:
          try:
            muestraFallo ('FIXME: Condacto desconocido', 'Código de condacto: ' + str (num_condacto) + '\nProceso: ' + str (num_proceso) + '\nÍndice de entrada: ' + str (num_entrada))
          except:
            prn ('FIXME: Número de condacto', num_condacto, 'desconocido, en entrada', num_entrada, 'del proceso', num_proceso)
          return
        for i in range (len (condactos[num_condacto][1])):
          parametros.append (carga_int1())
        entrada.append ((condacto, parametros))
      entradas.append (entrada)
    if len (cabeceras) != len (entradas):
      prn ('ERROR: Número distinto de cabeceras y entradas para una tabla de',
           'procesos')
      return
    tablas_proceso.append ((cabeceras, entradas))

# Carga el vocabulario
def cargaVocabulario ():
  # Vamos a la posición del vocabulario
  fich_ent.seek (carga_desplazamiento (CAB_POS_VOCAB))
  # Cargamos cada palabra de vocabulario
  while True:
    caracter = carga_int1()
    if caracter == 0:  # Fin del vocabulario
      return
    caracter ^= 255
    if (caracter < 16) or (caracter > 31):
      palabra = [chr (caracter)]
    else:
      palabra = [daad_a_chr[caracter - 16]]
    for i in range (4):
      caracter = carga_int1() ^ 255
      palabra.append (chr (caracter))
    # SWAN guarda las palabras de menos de cinco letras con espacios al final
    # SWAN guarda las palabras en mayúsculas
    vocabulario.append ((''.join (palabra).rstrip().lower(), carga_int1(), carga_int1()))

# Prepara la configuración sobre la plataforma
def preparaPlataforma ():
  global alinear, carga_int2, despl_ini, guarda_int2, plataforma
  # Cargamos la versión del formato de base de datos y el identificador de plataforma
  fich_ent.seek (CAB_PLATAFORMA)
  plataforma = carga_int2_be()
  # Detectamos "endianismo"
  if plataforma / 256 > plataforma & 255:  # Es Little Endian
    carga_int2 = carga_int2_le
    bajo_nivel_cambia_endian (le = True)
  else:
    carga_int2 = carga_int2_be
    bajo_nivel_cambia_endian (le = False)
  # Detectamos si habrá paddings para mantener los desplazamientos en posiciones pares
  if plataforma in plats_word:
    alinear = True
    # Habrá padding en la posición 9 de la cabecera
    for variable in globals():
      if variable[:8] == 'CAB_POS_':
        globals()[variable] += 1  # Incrementaremos en uno todas las entradas de offsets en la cabecera
  # Preparamos el desplazamiento inicial para carga desde memoria
  if plataforma in despl_ini_plat:
    despl_ini = despl_ini_plat[plataforma]
    if type (despl_ini) != int:
      # Detectamos la diferencia de desplazamiento, al ser el identificador de plataforma ambiguo
      fich_ent.seek (CAB_LONG_FICH)
      longitud = carga_int2()
      for difPosible in despl_ini:
        for posicion in range (CAB_POS_ABREVS, CAB_LONG_FICH, 2):
          fich_ent.seek (posicion)
          despl = carga_int2()
          if despl and despl - difPosible == longitud:  # Lo tenemos, esta es la diferencia
            break
        else:  # No es esta la diferencia
          continue
        break  # Ya encontrada
      despl_ini = difPosible
    bajo_nivel_cambia_despl (despl_ini)
