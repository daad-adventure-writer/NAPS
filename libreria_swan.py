# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Librería de SWAN (parte común a editor, compilador e intérprete)
# Copyright (C) 2020-2022 José Manuel Ferrer Ortiz
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
# Nombres de los tipos de palabra (para el IDE)
TIPOS_PAL = ('Verbo', 'Adverbio', 'Nombre', 'Adjetivo', 'Preposición', 'Conjunción', 'Pronombre')


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
  # código : (nombre, número_parámetros, es_acción)
    0 : ('AT',      1, False),
    1 : ('NOTAT',   1, False),
    2 : ('ATGT',    1, False),
    3 : ('ATLT',    1, False),
    4 : ('PRESENT', 1, False),
    5 : ('ABSENT',  1, False),
    6 : ('WORN',    1, False),
    7 : ('NOTWORN', 1, False),
    8 : ('CARRIED', 1, False),
    9 : ('NOTCARR', 1, False),
   10 : ('CHANCE',  1, False),
   11 : ('ZERO',    1, False),
   12 : ('NOTZERO', 1, False),
   13 : ('EQ',      2, False),
   14 : ('GT',      2, False),
   15 : ('LT',      2, False),
   16 : ('ADJECT1', 1, False),
   17 : ('ADVERB',  1, False),
   # 18 : ('_18_',    0, True),   # Formerly INVEN
   19 : ('DESC',    0, True),
   20 : ('QUIT',    0, False),  # Se comporta como condición, no satisfecha si no termina
   21 : ('END',     0, True),
   22 : ('DONE',    0, True),
   23 : ('OK',      0, True),
   24 : ('ANYKEY',  0, True),
   25 : ('SAVE',    0, True),
   26 : ('LOAD',    0, True),
   27 : ('TURNS',   0, True),
   28 : ('SCORE',   0, True),
   # 29 : ('_29_',    0, True),   # Formerly CLS
   30 : ('DROPALL', 0, True),
   31 : ('AUTOG',   0, True),
   32 : ('AUTOD',   0, True),
   33 : ('AUTOW',   0, True),
   34 : ('AUTOR',   0, True),
   35 : ('PAUSE',   1, True),
   36 : ('TIMEOUT', 0, False),
   37 : ('GOTO',    1, True),
   38 : ('MESSAGE', 1, True),
   39 : ('REMOVE',  1, True),
   40 : ('GET',     1, True),
   41 : ('DROP',    1, True),
   42 : ('WEAR',    1, True),
   43 : ('DESTROY', 1, True),
   44 : ('CREATE',  1, True),
   45 : ('SWAP',    2, True),
   46 : ('PLACE',   2, False),  # Se comporta como condición: cuando se intenta poner un objeto en 255, termina como condición no cumplida
   47 : ('SET',     1, True),
   48 : ('CLEAR',   1, True),
   49 : ('PLUS',    2, True),
   50 : ('MINUS',   2, True),
   51 : ('LET',     2, True),
   52 : ('NEWLINE', 0, True),
   53 : ('PRINT',   1, True),
   54 : ('SYSMESS', 1, True),
   55 : ('ISAT',    2, False),
   56 : ('COPYOF',  2, True),
   57 : ('COPYOO',  2, True),
   58 : ('COPYFO',  2, True),
   59 : ('COPYFF',  2, True),
   60 : ('LISTOBJ', 0, True),
   # 61 : ('_61_',    0, True),   # Formerly EXTERN
   62 : ('RAMSAVE', 0, True),
   63 : ('RAMLOAD', 1, True),
   # 64 : ('_64_',    0, True),   # Formerly BEEP/BELL
   # 65 : ('_65_',    0, True),   # Formerly PAPER
   # 66 : ('_66_',    0, True),   # Formerly INK
   # 67 : ('_67_',    0, True),   # Formerly BORDER
   68 : ('PREP',    1, False),
   69 : ('NOUN2',   1, False),
   70 : ('ADJECT2', 1, False),
   71 : ('ADD',     2, True),
   72 : ('SUB',     2, True),
   73 : ('PARSE',   0, True),
   74 : ('LISTAT',  1, True),
   75 : ('PROCESS', 1, True),
   76 : ('SAME',    2, False),
   77 : ('MES',     1, True),
   # 78 : ('_78_',    0, True),   # Formerly CHARSET
   79 : ('NOTEQ',   2, False),
   80 : ('NOTSAME', 2, False),
   # 81 : ('_81_',    0, True),   # Formerly MODE
   # 82 : ('_82_',    0, True),   # Formerly LINE
   # 83 : ('_83_',    0, True),   # Formerly TIME
   # 84 : ('_84_',    0, True),   # Formerly PICTURE
   85 : ('DOALL',   1, True),
   # 86 : ('_86_',    0, True),   # Formerly PROMPT
   # 87 : ('_87_',    0, True),   # Formerly GRAPHIC
   88 : ('ISNOTAT', 2, False),
   89 : ('WEIGH',   2, True),
   90 : ('PUTIN',   2, True),
   91 : ('TAKEOUT', 2, True),
   92 : ('NEWTEXT', 0, True),
   # 93 : ('_93_',    0, True),   # Formerly ABILITY
   94 : ('WEIGHT',  1, True),
   95 : ('RANDOM',  1, True),
   # 96 : ('_96_',    0, True),   # Formerly INPUT
   # 97 : ('_97_',    0, True),   # Formerly SAVEAT
   # 98 : ('_98_',    0, True),   # Formerly BACKAT
   # 99 : ('_99_',    0, True),   # Formerly PRINTAT
  100 : ('WHATO',   0, True),
  # 101 : ('_101_',   0, True),   # Formerly RESET
  102 : ('PUTO',    1, True),
  103 : ('NOTDONE', 0, True),
  104 : ('AUTOP',   1, True),
  105 : ('AUTOT',   1, True),
  106 : ('MOVE',    1, False),  # Se comporta como condición
  # 107 : ('_107_',   0, True),   # Formerly PROTECT
  # Desde aquí, todos estos son nuevos en SWAN
  108 : ('OAT',     2, False),
  109 : ('FGET',    2, True),
  110 : ('FPUT',    2, True),
  111 : ('FMES',    1, True),
  112 : ('SETB',    2, True),
  113 : ('CLEARB',  2, True),
  114 : ('BSET',    2, False),
  115 : ('NOTBSET', 2, False),
  116 : ('NOTOAT',  2, False),
  117 : ('OOPSAVE', 0, True),
  118 : ('OOPS',    1, True),
  119 : ('GON',     0, True),
  120 : ('GOFF',    0, True),
  121 : ('OVERLAY', 1, True),
  122 : ('COMMAND', 0, True),
  123 : ('CSAVE',   0, True),
  124 : ('CLOAD',   0, True),
}


# Funciones que utiliza el IDE o el intérprete directamente

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
    prepara_plataforma()
    carga_abreviaturas()
    carga_cadenas (CAB_NUM_LOCS,     CAB_POS_LST_POS_LOCS,     desc_locs)
    carga_cadenas (CAB_NUM_OBJS,     CAB_POS_LST_POS_OBJS,     desc_objs)
    carga_cadenas (CAB_NUM_MSGS_USR, CAB_POS_LST_POS_MSGS_USR, msgs_usr)
    carga_cadenas (CAB_NUM_MSGS_SYS, CAB_POS_LST_POS_MSGS_SYS, msgs_sys)
    carga_atributos()
    carga_conexiones()
    carga_localidades_objetos()
    carga_vocabulario()
    carga_nombres_objetos()
    carga_tablas_procesos()
  except:
    return False

def escribe_secs_ctrl (cadena):
  """Devuelve la cadena dada convirtiendo la representación de secuencias de control en sus códigos"""
  # TODO: implementar
  return cadena

def lee_secs_ctrl (cadena, QChar):
  """Devuelve la cadena dada convirtiendo las secuencias de control en una representación imprimible"""
  return cadena.replace ('\\', '\\\\').replace ('\n', '\\n')


# Funciones de apoyo de alto nivel

# Carga las abreviaturas
def carga_abreviaturas ():
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
def carga_atributos ():
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
def carga_cadenas (pos_num_cads, pos_lista_pos, cadenas):
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
def carga_conexiones ():
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

def carga_localidades_objetos ():
  """Carga las localidades iniciales de los objetos (dónde está cada uno)"""
  # Vamos a la posición de las localidades de los objetos
  fich_ent.seek (carga_desplazamiento (CAB_POS_LOCS_OBJS))
  # Cargamos la localidad de cada objeto
  for i in range (num_objetos[0]):
    locs_iniciales.append (carga_int1())

def carga_nombres_objetos ():
  """Carga los nombres y adjetivos de los objetos"""
  # Vamos a la posición de los nombres de los objetos
  fich_ent.seek (carga_desplazamiento (CAB_POS_NOMS_OBJS))
  # Cargamos el nombre y adjetivo de cada objeto
  for i in range (num_objetos[0]):
    nombres_objs.append ((carga_int1(), carga_int1()))

# Carga las tablas de procesos
# El proceso 0 es la tabla de respuestas
# En los procesos 1 y 2, las cabeceras de las entradas se ignoran
def carga_tablas_procesos ():
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
        for i in range (condactos[num_condacto][1]):
          parametros.append (carga_int1())
        entrada.append ((condacto, parametros))
      entradas.append (entrada)
    if len (cabeceras) != len (entradas):
      prn ('ERROR: Número distinto de cabeceras y entradas para una tabla de',
           'procesos')
      return
    tablas_proceso.append ((cabeceras, entradas))

# Carga el vocabulario
def carga_vocabulario ():
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
def prepara_plataforma ():
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
