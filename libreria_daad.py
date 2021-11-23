# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Librería de DAAD (parte común a editor, compilador e intérprete)
# Copyright (C) 2010, 2013, 2018-2021 José Manuel Ferrer Ortiz
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

import os
import sys  # Para stderr


# Variables que se exportan (fuera del paquete)

# Ponemos los módulos de condactos en orden, para permitir que las funciones de los condactos de igual firma (nombre, tipo y número de parámetros) de los sistemas más nuevos tengan precedencia sobre las de sistemas anteriores
mods_condactos = ('condactos_daad', 'condactos_paws', 'condactos_quill')

atributos       = []   # Atributos de los objetos
atributos_extra = []   # Atributos extra de los objetos
conexiones      = []   # Listas de conexiones de cada localidad
desc_locs       = []   # Descripciones de las localidades
desc_objs       = []   # Descripciones de los objetos
locs_iniciales  = []   # Localidades iniciales de los objetos
msgs_sys        = []   # Mensajes de sistema
msgs_usr        = []   # Mensajes de usuario
nombres_objs    = []   # Nombre y adjetivo de los objetos
num_objetos     = [0]  # Número de objetos (en lista para pasar por referencia)
tablas_proceso  = []   # Tablas de proceso
vocabulario     = []   # Vocabulario

# Lista de funciones que importan bases de datos desde ficheros, con sus extensiones soportadas y descripción del tipo de fichero
funcs_exportar = (('guarda_bd', ('ddb',), 'Bases de datos DAAD'), )
funcs_importar = (('carga_bd',  ('ddb',), 'Bases de datos DAAD'), )
# Función que crea una nueva base de datos (vacía)
func_nueva = ''


# Constantes que se exportan (fuera del paquete)

EXT_SAVEGAME   = 'agp'   # Extensión para las partidas guardadas
INDIRECCION    = True    # El parser soporta indirección (para el IDE)
LONGITUD_PAL   = 5       # Longitud máxima para las palabras de vocabulario
NOMBRE_SISTEMA = 'DAAD'  # Nombre de este sistema
NUM_ATRIBUTOS  = [2]     # Número de atributos de objeto
NUM_BANDERAS   = 256     # Número de banderas del parser
# Nombres de los tipos de palabra (para el IDE)
TIPOS_PAL = ('Verbo', 'Adverbio', 'Nombre', 'Adjetivo', 'Preposición', 'Conjunción', 'Pronombre')


# Desplazamientos (offsets/posiciones) en la cabecera
CAB_VERSION               =  0  # Versión del formato de base de datos
CAB_PLATAFORMA            =  1  # Identificador de plataforma e idioma
CAB_NUM_OBJS              =  3  # Número de objetos
CAB_NUM_LOCS              =  4  # Número de localidades
CAB_NUM_MSGS_USR          =  5  # Número de mensajes de usuario
CAB_NUM_MSGS_SYS          =  6  # Número de mensajes de sistema
CAB_NUM_PROCS             =  7  # Número de procesos
CAB_POS_ABREVS            =  8  # Posición de las abreviaturas
CAB_POS_LST_POS_PROCS     = 10  # Posición lista de posiciones de procesos
CAB_POS_LST_POS_OBJS      = 12  # Posición lista de posiciones de objetos
CAB_POS_LST_POS_LOCS      = 14  # Posición lista de posiciones de localidades
CAB_POS_LST_POS_MSGS_USR  = 16  # Pos. lista de posiciones de mensajes de usuario
CAB_POS_LST_POS_MSGS_SYS  = 18  # Pos. lista de posiciones de mensajes de sistema
CAB_POS_LST_POS_CNXS      = 20  # Posición lista de posiciones de conexiones
CAB_POS_VOCAB             = 22  # Posición del vocabulario
CAB_POS_LOCS_OBJS         = 24  # Posición de localidades iniciales de objetos
CAB_POS_NOMS_OBJS         = 26  # Posición de los nombres de los objetos
CAB_POS_ATRIBS_OBJS       = 28  # Posición de los atributos de los objetos
CAB_POS_ATRIBS_EXTRA_OBJS = 30  # Posición de los atributos extra de los objetos
CAB_LONG_FICH             = 30  # Longitud de la base de datos

alinear        = False  # Si alineamos con relleno (padding) las listas de desplazamientos a posiciones pares
compatibilidad = True   # Modo de compatibilidad con los intérpretes originales
despl_ini      = 0      # Desplazamiento inicial para cargar desde memoria
nueva_version  = []     # Si la base de datos es de las últimas versiones de DAAD, vacío = no
plataforma     = None   # Número de plataforma en la base de datos

# TODO: usar identificadores de plataforma independientes del idioma (0: PC, 1: Spectrum, etc.)
# Desplazamientos iniciales para cargar desde memoria, de las plataformas en las que éste no es 0
# Si el valor está en una lista, será una cota inferior, y se auto-detectará este desplazamiento
despl_ini_plat = {
  17:  [33600],  # Spectrum 48K
  113: 256,      # Amstrad PCW
}
plats_detectarLE = (1,)       # Plataformas que podrían ser tanto BE como LE, en formato 2 (PC)
plats_LE         = (17, 113)  # Plataformas que son Little Endian (Spectrum 48K y Amdstrad PCW)
plats_word       = (1,)       # Plataformas que no pueden leer words en desplazamientos impares (PC)

# Tabla de conversión de caracteres, posiciones 16-31 (inclusive)
daad_a_chr = ('ª', '¡', '¿', '«', '»', 'á', 'é', 'í', 'ó', 'ú', 'ñ', 'Ñ', 'ç', 'Ç', 'ü', 'Ü')


# Diccionarios de condactos

condactos = {
  # El formato es el siguiente:
  # código : (nombre, número_parámetros, es_acción)
  # XXX: marco temporalmente, tras la coma, los que cuentan para proceso_acc o no, con #s/n
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
   18 : ('INVEN',   0, True),   # Implementado en intérprete de Jabato EGA
   19 : ('DESC',    0, True),
   20 : ('QUIT',    0, False),  # Se comporta como condición, no satisfecha si no termina
   21 : ('END',     0, True),
   22 : ('DONE',    0, True),
   23 : ('OK',      0, True),
   24 : ('ANYKEY',  0, True),
   25 : ('SAVE',    0, True),
   26 : ('LOAD',    0, False),  # Se comporta como condición, satisfecha si carga bien
   27 : ('TURNS',   0, True),
   28 : ('DISPLAY', 1, True),   # Era SCORE
   29 : ('CLS',     0, True),
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
   46 : ('PLACE',   2, False),  # Se comporta como condición: al intentar poner un objeto en 255, termina como condición no cumplida
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
   61 : ('EXTERN',  2, True),
   62 : ('RAMSAVE', 0, True),
   63 : ('RAMLOAD', 1, False),  # Se comporta como condición, satisfecha si carga bien
   64 : ('BEEP',    2, True),
   65 : ('PAPER',   1, True),
   66 : ('INK',     1, True),
   67 : ('BORDER',  1, True),
   68 : ('PREP',    1, False),
   69 : ('NOUN2',   1, False),
   70 : ('ADJECT2', 1, False),
   71 : ('ADD',     2, True),
   72 : ('SUB',     2, True),
   73 : ('PARSE',   0, False),  # Se comporta como condición, satisfecha si no hay frase válida
   74 : ('LISTAT',  1, True),
   75 : ('PROCESS', 1, True),
   76 : ('SAME',    2, False),
   77 : ('MES',     1, True),
   78 : ('WINDOW',  1, True),   # Era CHARSET
   79 : ('NOTEQ',   2, False),
   80 : ('NOTSAME', 2, False),
   81 : ('MODE',    1, True),
   82 : ('WINAT',   2, True),   # Era LINE
   83 : ('TIME',    2, True),
   84 : ('PICTURE', 1, True),
   85 : ('DOALL',   1, True),
   86 : ('PROMPT',  1, True),
   87 : ('GFX',     2, True),   # Era GRAPHIC
   88 : ('ISNOTAT', 2, False),
   89 : ('WEIGH',   2, True),
   90 : ('PUTIN',   2, True),
   91 : ('TAKEOUT', 2, True),
   92 : ('NEWTEXT', 0, True),
   93 : ('ABILITY', 2, True),
   94 : ('WEIGHT',  1, True),
   95 : ('RANDOM',  1, True),
   96 : ('INPUT',   2, True),
   97 : ('SAVEAT',  0, True),
   98 : ('BACKAT',  0, True),
   99 : ('PRINTAT', 2, True),
  100 : ('WHATO',   0, True),
  101 : ('CALL',    1, True),   # Era RESET. Tal vez tome dos bytes para un desplazamiento
  102 : ('PUTO',    1, True),
  103 : ('NOTDONE', 0, True),
  104 : ('AUTOP',   1, True),
  105 : ('AUTOT',   1, True),
  106 : ('MOVE',    1, False),  # Se comporta como condición
  107 : ('WINSIZE', 2, True),   # Era PROTECT
  108 : ('REDO',    0, True),
  109 : ('CENTRE',  0, True),
  110 : ('EXIT',    1, True),
  111 : ('INKEY',   0, False),
  112 : ('SMALLER', 2, False),  # Del revés a como está en el manual
  113 : ('BIGGER',  2, False),  # Del revés a como está en el manual
  114 : ('ISDONE',  0, False),
  115 : ('ISNDONE', 0, False),
  116 : ('SKIP',    1, True),
  117 : ('RESTART', 0, True),
  118 : ('TAB',     1, True),
  119 : ('COPYOF',  2, True),
  121 : ('COPYOO',  2, True),
  123 : ('COPYFO',  2, True),
  125 : ('COPYFF',  2, True),
  126 : ('COPYBF',  2, True),
  127 : ('RESET',   0, True),
}

# Reemplazo de condactos en nuevas versiones de DAAD
condactos_nuevos = {
  # El formato es el siguiente:
  # código : (nombre, número_parámetros, es_acción)
   18 : ('SFX',     2, True),   # Era INVEN
   19 : ('DESC',    1, True),
   25 : ('SAVE',    1, True),
   26 : ('LOAD',    1, False),  # Se comporta como condición, satisfecha si carga bien
   27 : ('DPRINT',  1, True),   # Era TURNS
   36 : ('SYNONYM', 2, True),   # Era TIMEOUT
   56 : ('SETCO',   1, True),   # Era COPYOF
   57 : ('SPACE',   0, True),   # Era COPYOO
   58 : ('HASAT',   1, False),  # Era COPYFO
   59 : ('HASNAT',  1, False),  # Era COPYFF
   73 : ('PARSE',   1, False),  # Se comporta como condición
   84 : ('PICTURE', 1, False),  # Se comporta como condición, en función si esa imagen existe
   86 : ('MOUSE',   1, True),   # Era PROMPT
}


# Funciones de apoyo de bajo nivel

# Guarda una cadena sin abreviar, en el formato de DAAD
def guarda_cadena (cadena):
  cuenta = 0
  for caracter in cadena:
    if ord (caracter) > 127:  # Conversión necesaria
      try:
        caracter = daad_a_chr.index (caracter) + 16
      except:
        cuenta += 1
        caracter = ord (caracter)
    elif caracter == '\n':
      caracter = ord ('\r')
    else:
      caracter = ord (caracter)
    guarda_int1 (caracter ^ 255)
  guarda_int1 (ord ('\n') ^ 255)  # Fin de cadena
  if cuenta:
    prn ('Error en guarda_cadena: la cadena "%s" tiene %d caracteres que exceden el código 127, pero no salen en daad_a_chr' %
        (cadena, cuenta))

# Guarda una cadena abreviada, en el formato de DAAD
def guarda_cadena_abreviada (cadena):
  for caracter in cadena:
    caracter = ord (caracter)
    guarda_int1 (caracter ^ 255)
  guarda_int1 (ord ('\n') ^ 255)  # Fin de cadena


# Funciones que utiliza el IDE directamente

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
    if version > 1:
      carga_atributos_extra()
      NUM_ATRIBUTOS[0] = 18
    carga_conexiones()
    carga_localidades_objetos()
    carga_vocabulario()
    carga_nombres_objetos()
    carga_tablas_procesos()
  except:
    return False

def nueva_bd ():
  """Crea una nueva base de datos de DAAD"""
  pass  # TODO: Por implementar


# Funciones de apoyo de alto nivel

def abrevia_cadenas ():
  """Abrevia las distintas cadenas abreviables"""
  global desc_locs_abrev, desc_objs_abrev, msgs_sys_abrev, msgs_usr_abrev
  desc_locs_abrev = []
  desc_objs_abrev = []
  msgs_sys_abrev  = []
  msgs_usr_abrev  = []
  for cadena in desc_locs:
    desc_locs_abrev.append (da_cadena_abreviada (cadena))
  if compatibilidad:
    for cadena in desc_objs:  # DC no los abrevia, porque no funciona bien en el intérprete
      desc_objs_abrev.append (cadena)
  else:
    for cadena in desc_objs:
      # XXX: ¿lista mal los objetos si se abrevian, al menos en la AO de PC (hace mal la conversión de su artículo)?
      desc_objs_abrev.append (da_cadena_abreviada (cadena))
  for cadena in msgs_sys:
    # FIXME: parece mostrar mal alguno de ellos si se abrevian, al menos en la AO de PC
    # tal vez abrevie mal
    msgs_sys_abrev.append (da_cadena_abreviada (cadena))
  for cadena in msgs_usr:
    msgs_usr_abrev.append (da_cadena_abreviada (cadena))

# Calcula y devuelve las abreviaturas óptimas, y la longitud de las cadenas tras aplicarse
# maxAbrev Longitud máxima de las abreviaturas
def calcula_abreviaturas (maxAbrev):
  global longAntes  # Longitud total de las cadenas antes de aplicar abreviaturas
  try:
    longAntes = longAntes
  except:
    longAntes = 0
  # prn (desc_locs)
  cadenas     = []  # Cadenas sobre las que aplicar abreviaturas
  longDespues = 0   # Longitud total de las cadenas tras aplicar abreviaturas, incluyendo espacio de éstas
  minAbrev    = 2   # Longitud mínima de las abreviaturas
  if compatibilidad:
    listasCadenas = (desc_locs, msgs_sys, msgs_usr)
  else:
    listasCadenas = (desc_locs, desc_objs, msgs_sys, msgs_usr)
  if not longAntes:
    for listaCadenas in listasCadenas:
      for cadena in listaCadenas:
        longCadena  = len (cadena) + 1
        longAntes  += longCadena
        cadenas.append(cadena)
    if compatibilidad:
      prn ('Longitud de cadenas sin abreviar (excluyendo objetos):', longAntes)
    else:
      prn ('Longitud de cadenas sin abreviar:', longAntes)
  else:
    for listaCadenas in listasCadenas:
      for cadena in listaCadenas:
        cadenas.append(cadena)
  # Tomamos las mejores abreviaturas
  num_abreviaturas = 128 if compatibilidad else 129
  optimas = []  # Abreviaturas óptimas calculadas
  for i in range (num_abreviaturas):
    # Calculamos cuántas veces aparece cada combinación
    ahorros     = {}  # Cuántos bytes en total se ahorrarían por abreviar cada ocurrencia
    ocurrencias = {}  # Cuántas veces aparece cada combinación de caracteres
    for cadena in cadenas:
      longCadena = len (cadena)
      if longCadena < minAbrev:
        continue
      for pos in range (0, (longCadena - minAbrev) + 1):
        for longAbrev in range (minAbrev, min (maxAbrev, longCadena - pos) + 1):
          ahorro     = longAbrev - 1
          ocurrencia = cadena[pos:pos + longAbrev]
          if ocurrencia in ocurrencias:
            ahorros[ocurrencia]     += ahorro
            ocurrencias[ocurrencia] += 1
          else:
            ahorros[ocurrencia]     = -1  # Con una ocurrencia, se desperdicia un byte por la referencia a la abreviatura
            ocurrencias[ocurrencia] = 1
    if not ahorros:  # Ya no hay más cadenas de longitud mínima
      break
    ordenAhorro = sorted(ahorros, key = ahorros.get, reverse = True)
    abreviatura = ordenAhorro[0]
    ahorro      = ahorros[abreviatura]
    # prn ((abreviatura, ahorro, ocurrencias[abreviatura]))
    # Buscamos superconjuntos entre el resto de combinaciones posibles
    maxAhorroSup = ahorro  # Ahorro máximo combinado por reemplazar abreviatura por un superconjunto, entre ambos
    maxSuperCjto = None
    posMaxAhorro = None
    sconjto      = None
    if i < 100:  # En las últimas, es poco probable que se aproveche esto
      for d in range (1, len (ordenAhorro)):  # Buscamos superconjuntos entre el resto de combinaciones posibles
        if abreviatura in ordenAhorro[d]:
          sconjto   = ordenAhorro[d]
          ahorroSup = ahorros[sconjto] + ((ocurrencias[abreviatura] - ocurrencias[sconjto]) * (len (abreviatura) - 1))
          if ahorroSup > maxAhorroSup:
            maxAhorroSup = ahorroSup
            maxSuperCjto = sconjto
            posMaxAhorro = d
            # prn ('"%s" (%d) es superconjunto de "%s", ahorros %d, ocurrencias %d. Ahorros combinados tomando éste %d' %
            #     (sconjto, d, abreviatura, ahorros[sconjto], ocurrencias[sconjto], ahorroSup))
    if posMaxAhorro:  # Tenía algún superconjunto (TODO: puede que siempre ocurra, si len (abreviatura) < maxAbrev)
      # prn ('La entrada "' + ordenAhorro[posMaxAhorro] + '" (' + str(posMaxAhorro) + ') reemplaza "' + abreviatura + '" (0)')
      abreviatura = maxSuperCjto
    # Añadimos esta abreviatura a la lista de abreviaturas óptimas calculadas
    ahorro = ahorros[abreviatura]
    if ahorro < 0:  # Ahorra más con 0 que con 1, seguramente por los superconjuntos
      break  # Ya no se ahorra nada más
    # prn ((abreviatura, ahorro, ocurrencias[abreviatura]))
    optimas.append((abreviatura, ahorro, ocurrencias[abreviatura]))
    longDespues += len (abreviatura)
    # Quitamos las ocurrencias de esta abreviatura en las cadenas
    c = 0
    nuevasCadenas = []
    while c < len (cadenas):
      partes = cadenas[c].split(abreviatura)
      if len (partes) > 1:
        cadenas[c] = partes[0]
        for p in range (1, len (partes)):
          nuevasCadenas.append (partes[p])
      c += 1
    cadenas += nuevasCadenas
  for cadena in cadenas:
    longCadena   = len (cadena) + 1
    longDespues += longCadena
  if len (optimas) < num_abreviaturas:
    longDespues += num_abreviaturas - len (optimas)  # Se reemplazarán por abreviaturas de un byte
  prn ('Con longitud m\xc3\xa1xima de las abreviaturas %d, longitud de cadenas tras abreviar: %d.' % (maxAbrev, longDespues))
  prn (optimas)
  nuevasAbreviaturas = []
  for abreviatura in optimas:
    nuevasAbreviaturas.append (abreviatura[0])
  return (nuevasAbreviaturas, longDespues)

# Carga las abreviaturas
def carga_abreviaturas ():
  global abreviaturas
  abreviaturas = []
  # Vamos a la posición de las abreviaturas
  posicion = carga_desplazamiento (CAB_POS_ABREVS)
  if posicion == 0:  # Sin abreviaturas. Como la segunda parte de El Jabato
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
      if (caracter < 16) or (caracter > 31):
        abreviatura.append (chr (caracter))
      else:
        abreviatura.append (daad_a_chr[caracter - 16])
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

# Carga los atributos extra de los objetos
def carga_atributos_extra ():
  # Vamos a la posición de los atributos de los objetos
  fich_ent.seek (carga_desplazamiento (CAB_POS_ATRIBS_EXTRA_OBJS))
  # Cargamos los atributos de cada objeto
  for i in range (num_objetos[0]):
    atributos_extra.append (carga_int2())  # FIXME: averiguar si su "endianismo" es fijo

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
      # Hay 129 abreviaturas, pero la 0 nunca se reemplaza por lo que tenga, sino por un espacio en blanco
      if (caracter >= 127) and abreviaturas:
        if compatibilidad and caracter - 127 == 0:
          cadena.append (' ')
        else:
          try:
            cadena.append (abreviaturas[caracter - 127])
          except:
            prn (caracter)
            raise
      elif caracter == ord ('\r'):  # Un carácter de nueva línea en la cadena
        cadena.append ('\n')
      elif (caracter < 16) or (caracter > 31):
        cadena.append (chr (caracter))
      else:
        cadena.append (daad_a_chr[caracter - 16])
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
      if (caracter < 16) or (caracter > 31):
        palabra.append (chr (caracter))
      else:
        palabra.append (daad_a_chr[caracter - 16])
    # DAAD guarda las palabras de menos de cinco letras con espacios al final
    # DAAD guarda las palabras en mayúsculas, salvo las tildes (en minúscula)
    vocabulario.append ((''.join (palabra).rstrip().lower(), carga_int1(),
                         carga_int1()))

def da_cadena_abreviada (cadena):
  """Devuelve una cadena abreviada, aplicándole las abreviaturas"""
  if not abreviaturas:
    return cadena
  # Realizamos los reemplazos de las abreviaturas, por orden de aparición de éstas
  partesCadena = [cadena]
  for a in range (len (abreviaturas)):
    abreviatura = abreviaturas[a]
    i = 0
    while i < len (partesCadena):
      parteCadena = partesCadena[i]
      if type (parteCadena) != str:
        i += 1
        continue
      partes = parteCadena.split(abreviatura)
      if len (partes) > 1:
        partesCadena[i] = partes[0]
        for p in range (1, len (partes)):
          partesCadena.insert(i + ((p - 1) * 2) + 1, (a, ))  # Guardamos el código de abreviatura en una tupla
          partesCadena.insert(i + ((p - 1) * 2) + 2, partes[p])
        i += p * 2
      i += 1
  # Juntamos todas las partes en una sola cadena abreviada
  abreviada = ''  # Forma abreviada de la cadena
  cuenta    = 0   # Caractéres inválidos, no debería ocurrir
  for parteCadena in partesCadena:
    if type (parteCadena) != str:
      abreviada += chr (127 + parteCadena[0])
      continue
    if not parteCadena:  # Cadena vacía
      continue
    for caracter in parteCadena:
      if ord (caracter) > 127:  # Conversión necesaria
        try:
          caracter = chr (daad_a_chr.index (caracter) + 16)
        except:
          cuenta += 1
      elif caracter == '\n':
        caracter = '\r'
      abreviada += caracter
  if cuenta:
    prn ('Error en da_cadena_abreviada: la cadena "%s" tiene %d caracteres que exceden el código 127, pero no salen en daad_a_chr' %
        (cadena, cuenta))
  return abreviada

def guardaAbreviaturas ():
  """Guarda la sección de abreviaturas sobre el fichero de salida, en caso de tenerlas, y devuelve cuántos bytes ocupa la sección"""
  if abreviaturas:  # Si hay abreviaturas...
    ocupado = 0
    for indice_abrev in range (129):  # ... habrá 129
      if indice_abrev >= len (abreviaturas):
        # TODO: sin modo compatibilidad no servirá esta
        abreviatura = chr (127)  # Abreviatura de relleno (una ya existente, de un byte)
      else:
        abreviatura = abreviaturas[indice_abrev]
      for pos in range (len (abreviatura)):
        caracter = abreviatura[pos]
        if ord (caracter) > 127:  # Conversión necesaria
          caracter = daad_a_chr.index (caracter) + 16
        else:
          caracter = ord (caracter)
        if pos == (len (abreviatura) - 1):
          caracter += 128
        guarda_int1 (caracter)
      ocupado += len (abreviatura)
    return ocupado
  return 0

# Almacena la base de datos entera en el fichero de salida, por orden de conveniencia, pero con vocabulario primero
# TODO: poner paddings
def guarda_bd_ (bbdd):
  global abreviaturas, fich_sal
  # longMin = 999999
  # for maxAbrev in range (3, 20):
  #   (posibles, longAbrev) = calcula_abreviaturas (maxAbrev)
  #   if longAbrev < longMin:
  #     if compatibilidad:
  #       abreviaturas = [chr (127)] + posibles
  #     else:
  #       abreviaturas = posibles
  #     longMin = longAbrev
  abrevia_cadenas()
  fich_sal     = bbdd
  num_locs     = len (desc_locs)       # Número de localidades
  num_msgs_usr = len (msgs_usr)        # Número de mensajes de usuario
  num_msgs_sys = len (msgs_sys)        # Número de mensajes de sistema
  num_procs    = len (tablas_proceso)  # Número de tablas de proceso
  bajo_nivel_cambia_sal (bbdd)
  guarda_int1 (1)             # Versión del formato
  guarda_int1 (plataforma)    # Identificador de plataforma
  guarda_int1 (95)            # No sé qué es, pero vale esto en las BBDD DAAD
  guarda_int1 (num_objetos[0])
  guarda_int1 (num_locs)
  guarda_int1 (num_msgs_usr)
  guarda_int1 (num_msgs_sys)
  guarda_int1 (num_procs)
  ocupado = 32  # Espacio ocupado hasta ahora (incluyendo la cabecera)
  # Reservamos espacio para el vocabulario
  pos_vocabulario = ocupado
  ocupado += (7 * len (vocabulario)) + 1
  # Posición de las abreviaturas
  if abreviaturas:
    guarda_desplazamiento (ocupado)
    for abreviatura in abreviaturas:
      ocupado += len (abreviatura)
  else:
    guarda_int2 (0)  # Sin abreviaturas
  # Posición de la lista de posiciones de los procesos
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_procs
  # Posición de la lista de posiciones de las descripciones de los objetos
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_objetos[0]
  # Posición de la lista de posiciones de las descripciones de las localidades
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_locs
  # Posición de la lista de posiciones de los mensajes de usuario
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_msgs_usr
  # Posición de la lista de posiciones de los mensajes de sistema
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_msgs_sys
  # Posición de la lista de posiciones de las conexiones
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_locs
  # Posición del vocabulario
  guarda_desplazamiento (pos_vocabulario)
  # Posición de las localidades de los objetos
  guarda_desplazamiento (ocupado)
  ocupado += num_objetos[0] + 1
  # Posición de los nombres de los objetos
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_objetos[0]
  # Posición de los atributos de los objetos
  guarda_desplazamiento (ocupado)
  ocupado += num_objetos[0]
  # Longitud del fichero
  guarda_int2 (0)  # Luego guardaremos el valor correcto (aún no lo sabemos)
  # Fin de la cabecera

  # Guardamos el vocabulario
  guardaVocabulario()
  # Guardamos las abreviaturas (si las hay)
  guardaAbreviaturas()
  # Guardamos las posiciones de las cabeceras de las tablas de proceso
  for tabla in tablas_proceso:
    guarda_desplazamiento (ocupado)
    ocupado += (4 * len (tabla[0])) + 2
  # Guardamos las posiciones de las descripciones de los objetos
  for i in range (num_objetos[0]):
    guarda_desplazamiento (ocupado)
    ocupado += len (desc_objs[i]) + 1
  # Guardamos las posiciones de las descripciones de las localidades
  for i in range (num_locs):
    guarda_desplazamiento (ocupado)
    ocupado += len (desc_locs_abrev[i]) + 1
  # Guardamos las posiciones de los mensajes de usuario
  ocupado += guardaPosMsgsUsr (ocupado)
  # Guardamos las posiciones de los mensajes de sistema
  ocupado += guardaPosMsgsSys (ocupado)
  # Guardamos las posiciones de las listas de conexiones de cada localidad
  for i in range (num_locs):
    guarda_desplazamiento (ocupado)
    ocupado += (2 * len (conexiones[i])) + 1
  # Guardamos las localidades iniciales de los objetos
  for localidad in locs_iniciales:
    guarda_int1 (localidad)
  guarda_int1 (255)  # Fin de la lista de localidades iniciales
  # Guardamos los nombres y adjetivos de los objetos
  for nombre, adjetivo in nombres_objs:
    guarda_int1 (nombre)
    guarda_int1 (adjetivo)
  # Guardamos los atributos de los objetos
  for atributo in atributos:
    guarda_int1 (atributo)
  # Guardamos las cabeceras de las tablas de proceso
  for cabeceras, entradas in tablas_proceso:
    for i in range (len (cabeceras)):
      guarda_int1 (cabeceras[i][0])  # Verbo
      guarda_int1 (cabeceras[i][1])  # Nombre
      guarda_desplazamiento (ocupado)
      try:
        for condacto, parametros in entradas[i]:
          ocupado += 1 + len (parametros)
      except:
        prn (entradas[i])
        raise
      ocupado += 1  # Por el fin de la entrada
    guarda_int2 (0)  # Fin del proceso (no tiene más entradas)
  # Guardamos las descripciones de los objetos
  guardaDescObjs()
  # Guardamos las descripciones de las localidades
  if abreviaturas:
    for descripcion in desc_locs_abrev:
      guarda_cadena_abreviada (descripcion)
  else:
    for descripcion in desc_locs:
      guarda_cadena (descripcion)
  # Guardamos los mensajes de usuario
  guardaMsgsUsr()
  # Guardamos los mensajes de sistema
  guardaMsgsSys()
  # Guardamos las listas de conexiones de cada localidad
  for lista in conexiones:
    for conexion in lista:
      guarda_int1 (conexion[0])
      guarda_int1 (conexion[1])
    guarda_int1 (255)  # Fin de las conexiones de esta localidad
  # Guardamos las entradas de las tablas de proceso
  for cabeceras, entradas in tablas_proceso:
    for entrada in entradas:
      for condacto, parametros in entrada:
        guarda_int1 (condacto)
        for parametro in parametros:
          guarda_int1 (parametro)
      guarda_int1 (255)  # Fin de la entrada
  # Guardamos la longitud final del fichero
  fich_sal.seek (CAB_LONG_FICH)
  guarda_desplazamiento (ocupado)

def guarda_bd (bbdd):
  """Almacena la base de datos entera en el fichero de salida, por orden de conveniencia"""
  global abreviaturas, fich_sal
  longMin = 999999
  for maxAbrev in range (3, 30):
    try:
      (posibles, longAbrev) = calcula_abreviaturas (maxAbrev)
    except KeyboardInterrupt:
      break
    if longAbrev < longMin:
      if compatibilidad:
        abreviaturas = [chr (127)] + posibles  # Hay que dejar eso como la primera abreviatura
      else:
        abreviaturas = posibles
      longMin = longAbrev  # Reducción máxima de longitud total de textos lograda
      longMax = maxAbrev   # Longitud máxima en la búsqueda de abreviaturas
  prn (longAntes - longMin, 'bytes ahorrados por abreviación de textos')
  prn ('La mejor combinación de abreviaturas se encontró con longitud máxima de abreviatura', longMax)
  prn (len (abreviaturas), 'abreviaturas en total, que son:')
  prn (abreviaturas)
  abrevia_cadenas()
  fich_sal     = bbdd
  num_locs     = len (desc_locs)       # Número de localidades
  num_msgs_usr = len (msgs_usr)        # Número de mensajes de usuario
  num_msgs_sys = len (msgs_sys)        # Número de mensajes de sistema
  num_procs    = len (tablas_proceso)  # Número de tablas de proceso
  bajo_nivel_cambia_sal (bbdd)
  guarda_int1 (version)       # Versión del formato
  guarda_int1 (plataforma)    # Identificador de plataforma
  guarda_int1 (95)            # No sé qué es, pero vale esto en las BBDD DAAD
  guarda_int1 (num_objetos[0])
  guarda_int1 (num_locs)
  guarda_int1 (num_msgs_usr)
  guarda_int1 (num_msgs_sys)
  guarda_int1 (num_procs)
  ocupado = 32  # Espacio ocupado hasta ahora (incluyendo la cabecera)
  if version > 1:
    ocupado += 2
  # Posición de las abreviaturas
  if abreviaturas:
    guarda_desplazamiento (ocupado)
    for abreviatura in abreviaturas:
      ocupado += len (abreviatura)
    if len (abreviaturas) < 129:
      ocupado += 129 - len (abreviaturas)
  else:
    guarda_int2 (0)  # Sin abreviaturas
  # Reservamos padding condicional para las plataformas que lo requieran
  if ocupado % 2 and alinear:
    ocupado += 1
    paddingTrasAbrev = True
  else:
    paddingTrasAbrev = False
  # Posición de la lista de posiciones de los procesos
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_procs
  # Posición de la lista de posiciones de las descripciones de los objetos
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_objetos[0]
  # Posición de la lista de posiciones de las descripciones de las localidades
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_locs
  # Posición de la lista de posiciones de los mensajes de usuario
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_msgs_usr
  # Posición de la lista de posiciones de los mensajes de sistema
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_msgs_sys
  # Posición de la lista de posiciones de las conexiones
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_locs
  # Posición del vocabulario
  guarda_desplazamiento (ocupado)
  ocupado += (7 * len (vocabulario)) + 1
  # Posición de las localidades de los objetos
  guarda_desplazamiento (ocupado)
  ocupado += num_objetos[0] + 1
  # Posición de los nombres de los objetos
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_objetos[0]
  # Posición de los atributos de los objetos
  guarda_desplazamiento (ocupado)
  ocupado += num_objetos[0]
  # Posición de los atributos extra de los objetos
  if version > 1:
    guarda_desplazamiento (ocupado)
    ocupado += 2 * num_objetos[0]
  # Longitud del fichero
  guarda_int2 (0)  # Luego guardaremos el valor correcto (aún no lo sabemos)
  # Fin de la cabecera

  # Guardamos las abreviaturas (si las hay)
  guardaAbreviaturas()
  # Añadimos padding condicional para las plataformas que lo requieran
  if paddingTrasAbrev:
    guarda_int1 (0)  # Relleno (padding)
  # Guardamos las posiciones de las cabeceras de las tablas de proceso
  for tabla in tablas_proceso:
    guarda_desplazamiento (ocupado)
    ocupado += (4 * len (tabla[0])) + 2
  # Guardamos las posiciones de las descripciones de los objetos
  for i in range (num_objetos[0]):
    guarda_desplazamiento (ocupado)
    ocupado += len (desc_objs_abrev[i]) + 1
  # Guardamos las posiciones de las descripciones de las localidades
  for i in range (num_locs):
    guarda_desplazamiento (ocupado)
    ocupado += len (desc_locs_abrev[i]) + 1
  # Guardamos las posiciones de los mensajes de usuario
  ocupado += guardaPosMsgsUsr (ocupado)
  # Guardamos las posiciones de los mensajes de sistema
  ocupado += guardaPosMsgsSys (ocupado)
  # Guardamos las posiciones de las listas de conexiones de cada localidad
  for i in range (num_locs):
    guarda_desplazamiento (ocupado)
    ocupado += (2 * len (conexiones[i])) + 1
  # Guardamos el vocabulario
  guardaVocabulario()
  # Guardamos las localidades iniciales de los objetos
  for localidad in locs_iniciales:
    guarda_int1 (localidad)
  guarda_int1 (255)  # Fin de la lista de localidades iniciales
  # Guardamos los nombres y adjetivos de los objetos
  for nombre, adjetivo in nombres_objs:
    guarda_int1 (nombre)
    guarda_int1 (adjetivo)
  # Guardamos los atributos de los objetos
  for atributo in atributos:
    guarda_int1 (atributo)
  # Guardamos los atributos extra de los objetos
  if version > 1:
    for atributo in atributos_extra:
      guarda_int2 (atributo)  # FIXME: averiguar si su "endianismo" es fijo
  # Guardamos las cabeceras de las tablas de proceso
  ahorroProcesos  = 0  # Ahorro por evitar repetir bloques de proceso iguales
  entradasProceso = dict()
  for cabeceras, entradas in tablas_proceso:
    for i in range (len (cabeceras)):
      guarda_int1 (cabeceras[i][0])  # Verbo
      guarda_int1 (cabeceras[i][1])  # Nombre
      for desplazamiento, entradaProceso in entradasProceso.items():
        if entradaProceso == entradas[i]:  # Ya había un bloque de proceso igual
          guarda_desplazamiento (desplazamiento)
          try:
            for condacto, parametros in entradas[i]:
              ahorroProcesos += 1 + len (parametros)
          except:
            # prn (entradas[i])  # Ya se habrá hecho esto la primera vez
            raise
          ahorroProcesos += 1  # Por el fin de la entrada
          break
      else:  # Bloque de entradas de proceso nuevo
        entradasProceso[ocupado] = entradas[i]
        guarda_desplazamiento (ocupado)
        try:
          for condacto, parametros in entradas[i]:
            ocupado += 1 + len (parametros)
        except:
          prn (entradas[i])
          raise
        ocupado += 1  # Por el fin de la entrada
      # prn (cabeceras[i], entradas[i])
    guarda_int2 (0)  # Fin del proceso (no tiene más entradas)
  prn (ahorroProcesos, 'bytes ahorrados por deduplicar bloques de proceso')
  # Guardamos las descripciones de los objetos
  guardaDescObjs()
  # Guardamos las descripciones de las localidades
  if abreviaturas:
    for descripcion in desc_locs_abrev:
      guarda_cadena_abreviada (descripcion)
  else:
    for descripcion in desc_locs:
      guarda_cadena (descripcion)
  # Guardamos los mensajes de usuario
  guardaMsgsUsr()
  # Guardamos los mensajes de sistema
  guardaMsgsSys()
  # Guardamos las listas de conexiones de cada localidad
  for lista in conexiones:
    for conexion in lista:
      guarda_int1 (conexion[0])
      guarda_int1 (conexion[1])
    guarda_int1 (255)  # Fin de las conexiones de esta localidad
  # Guardamos las entradas de las tablas de proceso
  entradasProceso = []
  for cabeceras, entradas in tablas_proceso:
    for entrada in entradas:
      if entrada in entradasProceso:
        continue  # Omitimos bloques duplicados
      entradasProceso.append(entrada)
      for condacto, parametros in entrada:
        guarda_int1 (condacto)
        for parametro in parametros:
          guarda_int1 (parametro)
      guarda_int1 (255)  # Fin de la entrada
  # Guardamos la longitud final del fichero
  fich_sal.seek (CAB_LONG_FICH)
  guarda_desplazamiento (ocupado)

def guardaDescObjs (posInicial = 0):
  """Guarda la sección de descripciones de los objetos sobre el fichero de salida, y devuelve cuántos bytes ocupa la sección, y las posiciones de cada descripción incluyendo posInicial"""
  return guardaMsgs (desc_objs, desc_objs_abrev, posInicial)

def guardaMsgs (msgs, msgsAbrev, posInicial = 0):
  """Guarda una sección de mensajes sobre el fichero de salida, y devuelve cuántos bytes ocupa la sección, y las posiciones de cada mensaje incluyendo posInicial"""
  ocupado    = 0
  posiciones = []
  if abreviaturas and msgsAbrev:
    for mensaje in msgsAbrev:
      posiciones.append (posInicial + ocupado)
      guarda_cadena_abreviada (mensaje)
      ocupado += len (mensaje) + 1
  else:
    for mensaje in msgs:
      posiciones.append (posInicial + ocupado)
      guarda_cadena (mensaje)
      ocupado += len (mensaje) + 1
  return ocupado, posiciones

def guardaMsgsSys (posInicial = 0):
  """Guarda la sección de mensajes de sistema sobre el fichero de salida, y devuelve cuántos bytes ocupa la sección, y las posiciones de cada mensaje incluyendo posInicial"""
  return guardaMsgs (msgs_sys, msgs_sys_abrev, posInicial)

def guardaMsgsUsr (posInicial = 0):
  """Guarda la sección de mensajes de usuario sobre el fichero de salida, y devuelve cuántos bytes ocupa la sección, y las posiciones de cada mensaje incluyendo posInicial"""
  return guardaMsgs (msgs_usr, msgs_usr_abrev, posInicial)

def guardaPosMsgs (msgs, msgsAbrev, pos):
  """Guarda una sección de posiciones de mensajes sobre el fichero de salida, y según el tipo del parámetro, devuelve cuántos bytes ocupa la sección o cuántos ocupan los mensajes

  El parámetro pos es la posición donde se guardará el primer mensaje, o bien una lista con la posición de cada mensaje. Si es el primer caso, la función devuelve cuánto ocupan los mensajes, y en el segundo caso, devuelve cuánto ocupa la sección"""
  if type (pos) == int:
    ocupado = 0
    if abreviaturas and msgsAbrev:
      msgs = msgsAbrev
    for i in range (len (msgs)):
      guarda_desplazamiento (pos + ocupado)
      ocupado += len (msgs[i]) + 1
    return ocupado
  # Es lista de posiciones de los mensajes
  for i in range (len (msgs)):
    guarda_desplazamiento (pos[i])
  return len (msgs) * 2

def guardaPosMsgsSys (pos):
  """Guarda la sección de posiciones de los mensajes de sistema sobre el fichero de salida, y según el tipo del parámetro, devuelve cuántos bytes ocupa la sección o cuántos ocupan los mensajes

  El parámetro pos es la posición donde se guardará el primer mensaje, o bien una lista con la posición de cada mensaje. Si es el primer caso, la función devuelve cuánto ocupan los mensajes, y en el segundo caso, devuelve cuánto ocupa la sección"""
  return guardaPosMsgs (msgs_sys, msgs_sys_abrev, pos)

def guardaPosMsgsUsr (pos):
  """Guarda la sección de posiciones de los mensajes de sistema sobre el fichero de salida, y según el tipo del parámetro, devuelve cuántos bytes ocupa la sección o cuántos ocupan los mensajes

  El parámetro pos es la posición donde se guardará el primer mensaje, o bien una lista con la posición de cada mensaje. Si es el primer caso, la función devuelve cuánto ocupan los mensajes, y en el segundo caso, devuelve cuánto ocupa la sección"""
  return guardaPosMsgs (msgs_usr, msgs_usr_abrev, pos)

def guardaVocabulario ():
  """Guarda la sección de vocabulario sobre el fichero de salida, y devuelve cuántos bytes ocupa la sección"""
  for palabra in vocabulario:
    # Rellenamos el texto de la palabra con espacios al final
    cadena = palabra[0].ljust (LONGITUD_PAL)
    for caracter in cadena:
      if ord (caracter) > 127:  # Conversión necesaria
        caracter = daad_a_chr.index (caracter) + 16
      else:
        caracter = ord (caracter.upper())
      guarda_int1 (caracter ^ 255)
    guarda_int1 (palabra[1])  # Código de la palabra
    guarda_int1 (palabra[2])  # Tipo de la palabra
  guarda_int1 (0)  # Fin del vocabulario
  return (len (vocabulario) * (LONGITUD_PAL + 2)) + 1

# Prepara la configuración sobre la plataforma
def prepara_plataforma ():
  global alinear, carga_int2, despl_ini, guarda_int2, plataforma, version, CAB_LONG_FICH
  # Cargamos la versión del formato de base de datos
  fich_ent.seek (CAB_VERSION)
  version = carga_int1()
  if version > 1:
    CAB_LONG_FICH += 2
    condactos.update (condactos_nuevos)
    nueva_version.append (True)
  # Cargamos el identificador de plataforma
  fich_ent.seek (CAB_PLATAFORMA)
  plataforma = carga_int1()

  # Preparamos el desplazamiento inicial para carga desde memoria
  detectar_despl = False
  if plataforma in despl_ini_plat:
    despl_ini = despl_ini_plat[plataforma]
    if type(despl_ini) == list:
      detectar_despl = True
      despl_ini      = despl_ini[0]

  # Detectamos "endianismo"
  le = False
  if plataforma in plats_LE:
    le = True
  elif version > 1 and plataforma in plats_detectarLE:
    asumidoLE = False
    sePasan   = 0  # Desplazamientos en la cabecera que exceden longitud real del fichero de BD
    # Si el fichero de base de datos tiene tamaño correcto, esta heurística bastará
    fich_ent.seek (CAB_LONG_FICH)
    longComoBE = carga_int2_be()
    fich_ent.seek (CAB_LONG_FICH)
    longComoLE = carga_int2_le()
    if longComoBE != long_fich_ent and longComoLE == long_fich_ent:
      asumidoLE = True
    else:  # Longitud del fichero de BD incorrecta
      fich_ent.seek (CAB_POS_ABREVS)
      for posCabecera in range (CAB_POS_ABREVS, CAB_LONG_FICH + 2, 2):
        desplazamiento = carga_int2_be()
        if (desplazamiento - despl_ini) > long_fich_ent:
          sePasan += 1
    if asumidoLE or sePasan > 2:
      le = True

  if le:
    carga_int2  = carga_int2_le
    guarda_int2 = guarda_int2_le
  else:
    carga_int2  = carga_int2_be
    guarda_int2 = guarda_int2_be
  if plataforma in plats_word:
    alinear = True

  if detectar_despl:
    tamCabecera = CAB_LONG_FICH + 2  # Longitud de la cabecera
    # Detectamos si hay 13 punteros de funciones externas, como ocurre en todas las aventuras de DAAD versión 2 menos las primeras
    fich_ent.seek (tamCabecera)
    ceros = 0
    for i in range (13):
      if carga_int2() == 0:
        ceros += 1
    if ceros > 6:
      tamCabecera += 26
    minimo = 999999
    fich_ent.seek (CAB_POS_ABREVS)
    for posCabecera in range (CAB_POS_ABREVS, tamCabecera, 2):
      desplazamiento = carga_int2()
      if not desplazamiento:  # Puede tener 0 en abreviaturas y funciones externas
        continue
      if desplazamiento < minimo:
        minimo = desplazamiento
    despl_ini = minimo - tamCabecera
    if tamCabecera > 34 and ceros < 13:
      # Puede haber código ensamblador entre la cabecera y donde apunta el primer puntero
      lista = []
      for reintentos in range (60):
        if validaPunteros (tamCabecera):
          break  # Todo ha cargado bien
        despl_ini -= 1
      else:
        prn ('Error: no se ha podido detectar el desplazamiento inicial de la base de datos', file = sys.stderr)
        sys.exit()
      if reintentos:
        prn ('Detectados', reintentos, 'bytes entre la cabecera y donde apunta su primer puntero', file = sys.stderr)

  bajo_nivel_cambia_despl  (despl_ini)
  bajo_nivel_cambia_endian (le)

def validaPunteros (tamCabecera):
  """Comprueba que los punteros en la base de datos apunten dentro de la misma"""
  # Comprobamos punteros en la cabecera
  fich_ent.seek (CAB_LONG_FICH)
  longitudBD = carga_int2() - despl_ini
  fich_ent.seek (CAB_POS_ABREVS)
  for posCabecera in range (CAB_POS_ABREVS, CAB_LONG_FICH, 2):
    desplazamiento = carga_int2() - despl_ini
    if desplazamiento >= longitudBD or desplazamiento < tamCabecera:
      return False

  # Comprobamos punteros de cabeceras de los procesos
  fich_ent.seek (CAB_NUM_PROCS)
  numProcs = carga_int1()
  # Vamos a la posición de la lista de posiciones de los procesos
  fich_ent.seek (CAB_POS_LST_POS_PROCS)
  fich_ent.seek (carga_int2() - despl_ini)
  posProcesos = []  # Posiciones de las cabeceras de los procesos
  for posTabla in range (numProcs):
    desplazamiento = carga_int2() - despl_ini
    if desplazamiento >= longitudBD or desplazamiento < tamCabecera:
      return False
    posProcesos.append (desplazamiento)

  # Comprobamos punteros de entradas de los procesos
  for posProceso in posProcesos:
    fich_ent.seek (posProceso)
    while True:
      verbo = carga_int1()
      if verbo == 0:  # Fin de este proceso
        break
      carga_int1()  # Nombre
      desplazamiento = carga_int2() - despl_ini
      if desplazamiento >= longitudBD or desplazamiento < tamCabecera:
        return False

  # XXX: continuar la implementación si fuera necesario, revisando más punteros
  return True

def inicializa_banderas (banderas):
  """Inicializa banderas con valores propios de DAAD"""
  # Banderas 0-28:
  # Comprobado con el intérprete DAAD de la versión EGA de Jabato, y el de Chichen Itzá:
  # Se inicializan todas a 0

  # Bandera 29:
  # Es posible que el bit 7 signifique que tenemos un modo gráfico (320x200),
  # con 53 columnas, en lugar de 80 (modo texto)
  # Comprobado con el intérprete DAAD de la versión EGA de Jabato:
  # - Con EGA-SVGA, se inicializa a 128
  # - Con Hercules, se inicializa a 0
  # Con el intérprete DAAD de Chichen Itzá, se inicializa al menos en algún modo gráfico, a 129
  if nueva_version:
    banderas[29] = 129
  else:
    banderas[29] = 128

  # Banderas 30-36:
  # Comprobado con el intérprete DAAD de la versión EGA de Jabato, y el de Chichen Itzá:
  # Se inicializan todas a 0

  # Bandera 37:
  # Comprobado con el intérprete DAAD de la versión EGA de Jabato: se inicializa a 4
  # Con el intérprete DAAD de Chichen Itzá: Se inicializa a 0
  if nueva_version:
    banderas[37] = 0

  # Bandera 38:
  # Comprobado con el intérprete DAAD de la versión EGA de Jabato, y el de Chichen Itzá:
  # Se inicializa a 0

  # Bandera 39:
  # En el intérprete DAAD de la Aventura Original: Se inicializa a 4
  # En el intérprete DAAD de la versión EGA de Jabato: Se inicializa a 13
  # En el intérprete DAAD de Chichen Itzá: Se inicializa a 0
  if not nueva_version:
    banderas[39] = 13

  # Banderas 40-45:
  # Comprobado con el intérprete DAAD de la versión EGA de Jabato, y el de Chichen Itzá:
  # Se inicializan todas a 0

  # Banderas 46 y 47:
  # Comprobado con el intérprete DAAD de la versión EGA de Jabato:
  # Se inicializan a 255
  # Con el intérprete DAAD de Chichen Itzá: Se inicializa a 0
  if nueva_version:
    banderas[46] = 0
    banderas[47] = 0

  # Banderas 48-51:
  # Comprobado con el intérprete DAAD de la versión EGA de Jabato, y el de Chichen Itzá:
  # Se inicializan todas a 0

  # Bandera 52:
  # Comprobado con el intérprete DAAD de la versión EGA de Jabato: Se inicializa a 10
  # Con el intérprete DAAD de Chichen Itzá: Se inicializa a 0
  if nueva_version:
    banderas[52] = 0

  # Banderas 53-61:
  # Comprobado con el intérprete DAAD de la versión EGA de Jabato, y el de Chichen Itzá:
  # Se inicializan todas a 0

  # Bandera 62:
  # Comprobado con el intérprete DAAD de la versión EGA de Jabato: Se inicializa a 0
  # Con el intérprete DAAD de Chichen Itzá: Se inicializa a 13 en EGA, y 141 en VGA
  if nueva_version:
    banderas[62] = 13

  # Banderas 63-254:
  # Comprobado con el intérprete DAAD de la versión EGA de Jabato, y el de Chichen Itzá:
  # Se inicializan todas a 0
