# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Librer�a de DAAD (parte com�n a editor, compilador e int�rprete)
# Copyright (C) 2010, 2013, 2018-2023 Jos� Manuel Ferrer Ortiz
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

# Ponemos los m�dulos de condactos en orden, para permitir que las funciones de los condactos de igual firma (nombre, tipo y n�mero de par�metros) de los sistemas m�s nuevos tengan precedencia sobre las de sistemas anteriores
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
num_objetos     = [0]  # N�mero de objetos (en lista para pasar por referencia)
tablas_proceso  = []   # Tablas de proceso
vocabulario     = []   # Vocabulario

# Lista de funciones que importan bases de datos desde ficheros, con sus extensiones soportadas y descripci�n del tipo de fichero
funcs_exportar = (('guarda_bd', ('ddb',), 'Bases de datos DAAD'), )
funcs_importar = (('carga_bd',              ('ddb',), 'Bases de datos DAAD'),
                  ('carga_sce',             ('sce',), 'C�digo fuente de DAAD tradicional'))
# Funci�n que crea una nueva base de datos (vac�a)
func_nueva = ''


# Constantes que se exportan (fuera del paquete)

EXT_SAVEGAME   = 'agp'   # Extensi�n para las partidas guardadas
INDIRECCION    = True    # El parser soporta indirecci�n (para el IDE)
LONGITUD_PAL   = 5       # Longitud m�xima para las palabras de vocabulario
NOMBRE_SISTEMA = 'DAAD'  # Nombre de este sistema
NUM_ATRIBUTOS  = [2]     # N�mero de atributos de objeto
NUM_BANDERAS   = 256     # N�mero de banderas del parser
NOMBRES_PROCS  = []      # Nombres de las primeras tablas de proceso (para el IDE)
# Nombres de los tipos de palabra (para el IDE)
TIPOS_PAL = ('Verbo', 'Adverbio', 'Nombre', 'Adjetivo', 'Preposicion', 'Conjuncion', 'Pronombre')
# Identificadores (para hacer el c�digo m�s legible) predefinidos
IDS_LOCS = {
  252: 'NOTCREATED',
       '_': 252,
  253: 'WORN',
       'WORN': 253,
  254: 'CARRIED',
       'CARRIED': 254,
  255: 'HERE',
       'HERE': 255}


# C�digo de cada tipo de palabra por nombre
tipos_pal_dict = {'verb': 0, 'adverb': 1, 'noun': 2, 'adjective': 3, 'preposition': 4, 'conjugation': 5, 'conjunction': 5, 'pronoun': 6}

# Desplazamientos (offsets/posiciones) en la cabecera
CAB_VERSION               =  0  # Versi�n del formato de base de datos
CAB_PLATAFORMA            =  1  # Identificador de plataforma e idioma
CAB_NUM_OBJS              =  3  # N�mero de objetos
CAB_NUM_LOCS              =  4  # N�mero de localidades
CAB_NUM_MSGS_USR          =  5  # N�mero de mensajes de usuario
CAB_NUM_MSGS_SYS          =  6  # N�mero de mensajes de sistema
CAB_NUM_PROCS             =  7  # N�mero de procesos
CAB_POS_ABREVS            =  8  # Posici�n de las abreviaturas
CAB_POS_LST_POS_PROCS     = 10  # Posici�n lista de posiciones de procesos
CAB_POS_LST_POS_OBJS      = 12  # Posici�n lista de posiciones de objetos
CAB_POS_LST_POS_LOCS      = 14  # Posici�n lista de posiciones de localidades
CAB_POS_LST_POS_MSGS_USR  = 16  # Pos. lista de posiciones de mensajes de usuario
CAB_POS_LST_POS_MSGS_SYS  = 18  # Pos. lista de posiciones de mensajes de sistema
CAB_POS_LST_POS_CNXS      = 20  # Posici�n lista de posiciones de conexiones
CAB_POS_VOCAB             = 22  # Posici�n del vocabulario
CAB_POS_LOCS_OBJS         = 24  # Posici�n de localidades iniciales de objetos
CAB_POS_NOMS_OBJS         = 26  # Posici�n de los nombres de los objetos
CAB_POS_ATRIBS_OBJS       = 28  # Posici�n de los atributos de los objetos
CAB_POS_ATRIBS_EXTRA_OBJS = 30  # Posici�n de los atributos extra de los objetos
CAB_LONG_FICH             = 30  # Longitud de la base de datos

alinear        = False  # Si alineamos con relleno (padding) las listas de desplazamientos a posiciones pares
compatibilidad = True   # Modo de compatibilidad con los int�rpretes originales
despl_ini      = 0      # Desplazamiento inicial para cargar desde memoria
nueva_version  = []     # Si la base de datos es de las �ltimas versiones de DAAD, vac�o = no
plataforma     = None   # N�mero de plataforma en la base de datos

# Desplazamientos iniciales para cargar desde memoria, de las plataformas en las que �ste no es 0
# Si el valor est� en una lista, ser� una cota inferior, y se auto-detectar� este desplazamiento
despl_ini_plat = {
  1: [33600],  # Spectrum 48K
  2: 14464,    # Commodore 64
  7: 256,      # Amstrad PCW
}
# Longitud m�xima de los ficheros de XMessages por plataforma
longitud_XMessages = {
  2:     2048,  # Commodore 64
  3:     2048,  # Amstrad CPC
  8:     2048,  # Commodore Plus/4
  15:   13684,  # MSX2
  None: 65536,  # Dem�s plataformas
}
plats_detectarLE = (0,)               # Plataformas que podr�an ser tanto BE como LE, en versi�n del formato 2 (PC)
plats_LE         = (1, 2, 7, 13, 15)  # Plataformas que son Little Endian (Spectrum 48K, Commodore 64, Amstrad PCW, PC VGA 256 y MSX2)
plats_word       = (0,)               # Plataformas que no pueden leer words en desplazamientos impares (PC)

# Tabla de conversi�n de caracteres, posiciones 16-31 (inclusive)
daad_a_chr = ('�', '�', '�', '�', '�', '�', '�', '�', '�', '�', '�', '�', '�', '�', '�', '�')


# Diccionarios de condactos

condactos = {
  # El formato es el siguiente:
  # c�digo : (nombre, par�metros, es_acci�n, flujo, versiones)
  # Donde:
  #   par�metros es una cadena con el tipo de cada par�metro
  #   flujo indica si el condacto cambia el flujo de ejecuci�n incondicionalmente, por lo que todo c�digo posterior en su entrada ser� inalcanzable
  #   versiones n�meros de versi�n de DAAD en las que existe condacto con ese nombre, c�digo y n�mero de par�metros. El valor 3 significa que existe en ambas versiones
  # Y los tipos de los par�metros se definen as�:
  # % : Porcentaje (percent), de 1 a 99 (TODO: comprobar si sirven 0 y 100)
  # f : N�mero de bandera (flagno), de 0 a NUM_BANDERAS - 1
  # i : Valor (value) entero con signo, de -127 a 128
  # j : N�mero de palabra de tipo adjetivo (adjective), � 255
  # l : N�mero de localidad (locno), de 0 a num_localidades - 1
  # L : N�mero de localidad (locno+), de 0 a num_localidades - 1, � 252-255
  # m : N�mero de mensaje de usuario (mesno), de 0 a num_msgs_usuario - 1
  # n : N�mero de palabra de tipo nombre (noun), � 255
  # o : N�mero de objeto (objno), de 0 a num_objetos - 1
  # p : N�mero de process (procno), de 0 a num_procesos - 1
  # r : N�mero de palabra de tipo preposici�n (preposition), � 255
  # s : N�mero de mensaje de sistema (sysno), de 0 a num_msgs_sistema - 1
  # u : Valor (value) entero sin signo, de 0 a 255
  # v : N�mero de palabra de tipo adverbio (adverb), � 255
  # V : N�mero de palabra de tipo verbo (verb), � 255
  # w : N�mero de subventana (stream), de 0 a 7
    0 : ('AT',      'l',  False, False, 3),
    1 : ('NOTAT',   'l',  False, False, 3),
    2 : ('ATGT',    'l',  False, False, 3),
    3 : ('ATLT',    'l',  False, False, 3),
    4 : ('PRESENT', 'o',  False, False, 3),
    5 : ('ABSENT',  'o',  False, False, 3),
    6 : ('WORN',    'o',  False, False, 3),
    7 : ('NOTWORN', 'o',  False, False, 3),
    8 : ('CARRIED', 'o',  False, False, 3),
    9 : ('NOTCARR', 'o',  False, False, 3),
   10 : ('CHANCE',  '%',  False, False, 3),
   11 : ('ZERO',    'f',  False, False, 3),
   12 : ('NOTZERO', 'f',  False, False, 3),
   13 : ('EQ',      'fu', False, False, 3),
   14 : ('GT',      'fu', False, False, 3),
   15 : ('LT',      'fu', False, False, 3),
   16 : ('ADJECT1', 'j',  False, False, 3),
   17 : ('ADVERB',  'v',  False, False, 3),
   18 : ('INVEN',   '',   True,  True,  1),  # Implementado en int�rprete de Jabato EGA
   19 : ('DESC',    '',   True,  True,  1),
   20 : ('QUIT',    '',   False, False, 3),  # Se comporta como condici�n, no satisfecha si no termina
   21 : ('END',     '',   True,  True,  3),
   22 : ('DONE',    '',   True,  True,  3),
   23 : ('OK',      '',   True,  True,  3),
   24 : ('ANYKEY',  '',   True,  False, 3),
   25 : ('SAVE',    '',   True,  False, 1),
   26 : ('LOAD',    '',   False, False, 1),  # Se comporta como condici�n, satisfecha si carga bien
   27 : ('TURNS',   '',   True,  False, 1),
   28 : ('DISPLAY', 'u',  True,  False, 3),  # Era SCORE
   29 : ('CLS',     '',   True,  False, 3),
   30 : ('DROPALL', '',   True,  False, 3),
   31 : ('AUTOG',   '',   True,  False, 3),
   32 : ('AUTOD',   '',   True,  False, 3),
   33 : ('AUTOW',   '',   True,  False, 3),
   34 : ('AUTOR',   '',   True,  False, 3),
   35 : ('PAUSE',   'u',  True,  False, 3),
   36 : ('TIMEOUT', '',   False, False, 1),
   37 : ('GOTO',    'l',  True,  False, 3),
   38 : ('MESSAGE', 'm',  True,  False, 3),
   39 : ('REMOVE',  'o',  True,  False, 3),
   40 : ('GET',     'o',  True,  False, 3),
   41 : ('DROP',    'o',  True,  False, 3),
   42 : ('WEAR',    'o',  True,  False, 3),
   43 : ('DESTROY', 'o',  True,  False, 3),
   44 : ('CREATE',  'o',  True,  False, 3),
   45 : ('SWAP',    'oo', True,  False, 3),
   46 : ('PLACE',   'oL', True,  False, 3),  # TODO: investigar m�s si en alg�n caso se comporta como condici�n
   47 : ('SET',     'f',  True,  False, 3),
   48 : ('CLEAR',   'f',  True,  False, 3),
   49 : ('PLUS',    'fu', True,  False, 3),
   50 : ('MINUS',   'fu', True,  False, 3),
   51 : ('LET',     'fu', True,  False, 3),
   52 : ('NEWLINE', '',   True,  False, 3),
   53 : ('PRINT',   'f',  True,  False, 3),
   54 : ('SYSMESS', 's',  True,  False, 3),
   55 : ('ISAT',    'oL', False, False, 3),
   56 : ('COPYOF',  'of', True,  False, 1),
   57 : ('COPYOO',  'oo', True,  False, 1),
   58 : ('COPYFO',  'fo', True,  False, 1),
   59 : ('COPYFF',  'ff', True,  False, 1),
   60 : ('LISTOBJ', '',   True,  False, 3),
   61 : ('EXTERN',  'uu', True,  False, 3),
   62 : ('RAMSAVE', '',   True,  False, 3),
   63 : ('RAMLOAD', 'f',  False, False, 3),  # Se comporta como condici�n, satisfecha si carga bien
   64 : ('BEEP',    'uu', True,  False, 3),
   65 : ('PAPER',   'u',  True,  False, 3),
   66 : ('INK',     'u',  True,  False, 3),
   67 : ('BORDER',  'u',  True,  False, 3),
   68 : ('PREP',    'r',  False, False, 3),
   69 : ('NOUN2',   'n',  False, False, 3),
   70 : ('ADJECT2', 'j',  False, False, 3),
   71 : ('ADD',     'ff', True,  False, 3),
   72 : ('SUB',     'ff', True,  False, 3),
   73 : ('PARSE',   '',   False, False, 1),  # Se comporta como condici�n, satisfecha si no hay frase v�lida
   74 : ('LISTAT',  'L',  True,  False, 3),
   75 : ('PROCESS', 'p',  True,  False, 3),
   76 : ('SAME',    'ff', False, False, 3),
   77 : ('MES',     'm',  True,  False, 3),
   78 : ('WINDOW',  'w',  True,  False, 3),  # Era CHARSET
   79 : ('NOTEQ',   'fu', False, False, 3),
   80 : ('NOTSAME', 'ff', False, False, 3),
   81 : ('MODE',    'u',  True,  False, 3),
   82 : ('WINAT',   'uu', True,  False, 3),  # Era LINE
   83 : ('TIME',    'uu', True,  False, 3),
   84 : ('PICTURE', 'u',  True,  False, 3),
   85 : ('DOALL',   'L',  True,  False, 3),
   86 : ('PROMPT',  's',  True,  False, 1),
   87 : ('GFX',     'uu', True,  False, 3),  # Era GRAPHIC
   88 : ('ISNOTAT', 'oL', False, False, 3),
   89 : ('WEIGH',   'of', True,  False, 3),
   90 : ('PUTIN',   'ol', True,  False, 3),
   91 : ('TAKEOUT', 'ol', True,  False, 3),
   92 : ('NEWTEXT', '',   True,  False, 3),
   93 : ('ABILITY', 'uu', True,  False, 3),
   94 : ('WEIGHT',  'f',  True,  False, 3),
   95 : ('RANDOM',  'f',  True,  False, 3),
   96 : ('INPUT',   'wu', True,  False, 3),
   97 : ('SAVEAT',  '',   True,  False, 3),
   98 : ('BACKAT',  '',   True,  False, 3),
   99 : ('PRINTAT', 'uu', True,  False, 3),
  100 : ('WHATO',   '',   True,  False, 3),
  101 : ('CALL',    'u',  True,  False, 3),  # Era RESET. Tal vez tome dos bytes para un desplazamiento
  102 : ('PUTO',    'L',  True,  False, 3),
  103 : ('NOTDONE', '',   True,  True,  3),
  104 : ('AUTOP',   'l',  True,  False, 3),
  105 : ('AUTOT',   'l',  True,  False, 3),
  106 : ('MOVE',    'f',  False, False, 3),  # Se comporta como condici�n
  107 : ('WINSIZE', 'uu', True,  False, 3),  # Era PROTECT
  108 : ('REDO',    '',   True,  False, 3),
  109 : ('CENTRE',  '',   True,  False, 3),
  110 : ('EXIT',    'u',  True,  True,  3),
  111 : ('INKEY',   '',   False, False, 3),
  112 : ('SMALLER', 'ff', False, False, 1),  # Del rev�s a como est� en el manual
  113 : ('BIGGER',  'ff', False, False, 1),  # Del rev�s a como est� en el manual
  114 : ('ISDONE',  '',   False, False, 3),
  115 : ('ISNDONE', '',   False, False, 3),
  116 : ('SKIP',    'i',  True,  True,  2),  # Nuevo en DAAD v2
  117 : ('RESTART', '',   True,  True,  3),
  118 : ('TAB',     'u',  True,  False, 3),
  119 : ('COPYOF',  'of', True,  False, 2),
  121 : ('COPYOO',  'oo', True,  False, 2),
  123 : ('COPYFO',  'fo', True,  False, 2),
  125 : ('COPYFF',  'ff', True,  False, 2),
  126 : ('COPYBF',  'ff', True,  False, 3),
  127 : ('RESET',   '',   True,  False, 3),
}

# Reemplazo de condactos en nuevas versiones de DAAD
condactos_nuevos = {
  # El formato es el siguiente:
  # c�digo : (nombre, par�metros, es_acci�n, flujo, versi�n)
   18 : ('SFX',     'uu', True,  False, 2),  # Era INVEN
   19 : ('DESC',    'l',  True,  False, 2),
   25 : ('SAVE',    'u',  True,  False, 2),
   26 : ('LOAD',    'u',  False, False, 2),  # Se comporta como condici�n, satisfecha si carga bien
   27 : ('DPRINT',  'f',  True,  False, 2),  # Era TURNS
   36 : ('SYNONYM', 'Vn', True,  False, 2),  # Era TIMEOUT
   56 : ('SETCO',   'o',  True,  False, 2),  # Era COPYOF
   57 : ('SPACE',   '',   True,  False, 2),  # Era COPYOO
   58 : ('HASAT',   'u',  False, False, 2),  # Era COPYFO
   59 : ('HASNAT',  'u',  False, False, 2),  # Era COPYFF
   73 : ('PARSE',   'u',  False, False, 2),  # Se comporta como condici�n
   84 : ('PICTURE', 'u',  False, False, 3),  # Se comporta como condici�n, en funci�n si esa imagen existe
   86 : ('MOUSE',   'u',  True,  False, 2),  # Era PROMPT
  112 : ('BIGGER',  'ff', False, False, 2),  # Mismo orden que en el manual
  113 : ('SMALLER', 'ff', False, False, 2),  # Mismo orden que en el manual
}


# Funciones que utiliza el IDE o el int�rprete directamente

def busca_partes (rutaCarpeta):
  """Analiza los ficheros en la carpeta dada, identificando por extensi�n y devuelviendo una lista con las bases de datos de las diferentes partes, y las bases de datos de gr�ficos correspondientes, para los diferentes modos gr�ficos encontrados"""
  # TODO: en PCW es parte???.*, y en SWAN es mindf???.*
  rutaCarpeta += '' if (rutaCarpeta[-1] == os.sep) else os.sep  # Asegura que termine con separador de directorio
  bd_gfx = {'cga': {}, 'ega': {}, 'dat': {}}
  partes = {}
  for nombreFichero in os.listdir (rutaCarpeta):
    nombreFicheroMin = nombreFichero.lower()
    if len (nombreFichero) != 9 or nombreFicheroMin[:4] != 'part' or nombreFichero[5] != '.':
      continue
    try:
      numParte = int (nombreFichero[4])
    except:
      continue
    extension = nombreFicheroMin[6:]
    modo      = None  # Modo gr�fico
    if extension == 'ddb':
      partes[numParte] = rutaCarpeta + nombreFichero
    elif extension in ('cgs', 'egs', 'scr'):  # Im�genes de portada
      if numParte != 1:
        continue
      if extension == 'scr':
        if os.path.getsize (rutaCarpeta + nombreFichero) == 16384:
          bd_gfx['cga'][0] = rutaCarpeta + nombreFichero
        else:
          bd_gfx['dat'][0] = rutaCarpeta + nombreFichero
      elif extension == 'cgs':
        bd_gfx['cga'][0] = rutaCarpeta + nombreFichero
      else:  # extension == 'egs'
        bd_gfx['ega'][0] = rutaCarpeta + nombreFichero
    elif extension in ('cga', 'dat', 'ega'):
      bd_gfx[extension][numParte] = rutaCarpeta + nombreFichero
  # Quitamos modos gr�ficos sin bases de datos gr�ficas para ellos
  for modo in tuple (bd_gfx.keys()):
    if not bd_gfx[modo]:
      del bd_gfx[modo]
  return partes, bd_gfx

def cadena_es_mayor (cadena1, cadena2):
  """Devuelve si la cadena1 es mayor a la cadena2 en el juego de caracteres de este sistema"""
  numeros = []  # Lista de c�digos de los caracteres de ambas cadenas
  for cadena in (cadena1, cadena2):
    codigos = []  # Lista de c�digos de los caracteres de la cadena actual
    for c in range (len (cadena)):
      if cadena[c] in daad_a_chr:
        codigos.append (daad_a_chr.index (cadena[c]) + 16)
      else:
        codigos.append (ord (cadena[c]))
    numeros.append (codigos)
  return numeros[0] > numeros[1]

# Carga la base de datos entera desde el fichero de entrada
# Para compatibilidad con el IDE:
# - Recibe como primer par�metro un fichero abierto
# - Recibe como segundo par�metro la longitud del fichero abierto
# - Devuelve False si ha ocurrido alg�n error
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
    if version > 1:
      cargaAtributosExtra()
      NUM_ATRIBUTOS[0] = 18
    cargaConexiones()
    cargaLocalidadesObjetos()
    cargaVocabulario()
    cargaNombresObjetos()
    cargaTablasProcesos()
  except:
    return False

def carga_sce (fichero, longitud):
  """Carga la base de datos desde el c�digo fuente SCE del fichero de entrada

  Para compatibilidad con el IDE:
  - Recibe como primer par�metro un fichero abierto
  - Recibe como segundo par�metro la longitud del fichero abierto
  - Devuelve False si ha ocurrido alg�n error"""
  global num_objetos, nueva_version
  try:
    import lark
  except:
    prn ('Para poder importar c�digo fuente, se necesita la librer�a Lark', 'versi�n <1.0' if sys.version_info[0] < 3 else '', file = sys.stderr)
    return False
  try:
    import re
    codigoSCE = fichero.read().replace (b'\r\n', b'\n').decode()
    # Procesamos carga de ficheros externos con directivas de preprocesador /LNK
    # TODO: extraer el c�digo com�n con abreFichXMessages, a funci�n en bajo_nivel
    # TODO: indicar nombre del fichero externo en errores ocurridos en �l, con n�mero de l�nea relativo a �l
    encaje = True
    while encaje:
      encaje = re.search ('\n/LNK[ \t]+([^ \n\t]+)', codigoSCE)
      if not encaje:
        break
      nombreFich = encaje.group (1).lower()
      if '.' not in nombreFich:
        nombreFich += '.sce'
      # Buscamos el fichero con independencia de may�sculas y min�sculas
      for nombreFichero in os.listdir (os.path.dirname (fichero.name)):
        if nombreFichero.lower() == nombreFich:
          nombreFich = nombreFichero
          break
      else:
        prn ('No se encuentra el fichero "' + nombreFich + '" requerido por una directiva de preprocesador /LNK', encaje.group (1), file = sys.stderr)
        return False
      try:
        ficheroLnk = open (os.path.join (os.path.dirname (fichero.name), nombreFich), 'rb')
      except:
        prn ('No se puede abrir el fichero "' + nombreFich + '" requerido por una directiva de preprocesador /LNK', encaje.group (1), file = sys.stderr)
        return False
      codigoSCE = codigoSCE[:encaje.start (0)] + ficheroLnk.read().replace (b'\r\n', b'\n').decode()
      ficheroLnk.close()
    parserSCE = lark.Lark.open ('gramatica_sce.lark', __file__, propagate_positions = True)
    arbolSCE  = parserSCE.parse (codigoSCE)
    # Cargamos cada tipo de textos
    for idSeccion, listaCadenas in (('stx', msgs_sys), ('mtx', msgs_usr), ('otx', desc_objs), ('ltx', desc_locs)):
      for seccion in arbolSCE.find_data (idSeccion):
        numEntrada = 0
        for entrada in seccion.find_data ('textentry'):
          numero = int (entrada.children[0])
          if numero != numEntrada:
            raise TabError ('n�mero de entrada %d en lugar de %d', (numEntrada, numero), entrada.meta)
          lineas = []
          for lineaTexto in entrada.children[1:]:
            if lineaTexto.type == 'COMMENT':
              continue  # Omitimos comentarios reconocidos por la gram�tica
            linea = str (lineaTexto)
            if not lineas and linea[:2] == '\n;':
              continue  # Omitimos comentarios iniciales
            lineas.append (linea[1:])  # El primer car�cter siempre ser� \n
          # Evitamos tomar nueva l�nea antes de comentario final como l�nea de texto en blanco
          if lineas and not linea and codigoSCE[lineaTexto.meta.start_pos + 1] == ';':
            del lineas[-1]
          for l in range (len (lineas) - 1, 0, -1):
            if lineas[l][:1] == ';':
              del lineas[l]  # Eliminamos comentarios finales
            else:
              break
          # Unimos las cadenas como corresponde
          cadena = ''
          for linea in lineas:
            if linea:
              cadena += ('' if cadena[-1:] in ('\n', '') else ' ') + linea
            else:
              cadena += '\n'
          listaCadenas.append (cadena)
          numEntrada += 1
    # Cargamos el vocabulario
    adjetivos = {'_': 255}
    nombres   = {'_': 255}
    verbos    = {'_': 255}
    for seccion in arbolSCE.find_data ('vocentry'):
      palabra = str (seccion.children[0])[:LONGITUD_PAL].lower()
      codigo  = int (seccion.children[1])
      tipo    = tipos_pal_dict[str (seccion.children[2].children[0]).lower()]
      vocabulario.append ((palabra, codigo, tipo))
      # Dejamos preparados diccionarios de c�digos de palabra para verbos, nombres y adjetivos
      if tipo == 0:
        verbos[palabra] = codigo
      elif tipo == 2:
        nombres[palabra] = codigo
        if codigo < 20:
          verbos[palabra] = codigo
      elif tipo == 3:
        adjetivos[palabra] = codigo
    # Cargamos datos de los objetos
    numEntrada = 0
    for seccion in arbolSCE.find_data ('objentry'):
      numero = int (seccion.children[0])
      if numero != numEntrada:
        raise TabError ('n�mero de objeto %d en lugar de %d', (numEntrada, numero), seccion.meta)
      # Cargamos la localidad inicial del objeto
      localidad = seccion.children[1].children[0]
      if localidad.type == 'INT':
        locs_iniciales.append (int (localidad))
      else:  # Valor no num�rico (p.ej. CARRIED)
        locs_iniciales.append (IDS_LOCS[str (localidad)])
      # Cargamos el peso del objeto
      entero = seccion.children[2]
      peso   = int (entero)
      if peso < 0 or peso > 63:
        raise TabError ('valor de peso del objeto %d entre 0 y 63', numEntrada, entero)
      # Cargamos los atributos del objeto
      valorAttrs = ''
      for atributo in seccion.find_data ('attr'):
        valorAttrs += '1' if atributo.children else '0'
      if len (valorAttrs) > 18:
        raise TabError ('N�mero de atributos para el objeto %d excesivo, NAPS s�lo soporta hasta 18', numEntrada, entero, 1)
      # Soportamos entre 2 y 18 atributos dejando a cero los que no se indiquen
      valorAttrs += '0' * (18 - len (valorAttrs))
      atributos.append (peso + ((valorAttrs[0] == '1') << 6) + ((valorAttrs[1] == '1') << 7))
      atributos_extra.append (int (valorAttrs[2:], 2))
      # Cargamos el vocabulario del objeto
      palabras = []
      for word in seccion.find_data ('word'):
        palabra = str (word.children[0])[:LONGITUD_PAL].lower() if word.children else '_'
        palabras.append (palabra)
        if len (palabras) == 1 and palabra not in nombres:
          break  # Para conservar la posici�n de la primera palabra inexistente
      if palabras[0] not in nombres or palabras[1] not in adjetivos:
        raise TabError ('una palabra de vocabulario de tipo %s', 'adjetivo' if len (palabras) > 1 else 'nombre', word.meta)
      nombres_objs.append ((nombres[palabras[0]], adjetivos[palabras[1]]))
      numEntrada += 1
    if numEntrada != len (desc_objs):
      raise TabError ('el mismo n�mero de objetos (%d) que de descripciones de objetos (%d)', (numEntrada, len (desc_objs)))
    num_objetos[0] = numEntrada
    # Preparamos c�digo y par�metros en cada versi�n, de los condactos, indexando por nombre
    datosCondactos = {}
    for listaCondactos in (condactos, condactos_nuevos):
      for codigo in listaCondactos:
        condacto = listaCondactos[codigo]
        if condacto[0] not in datosCondactos:
          datosCondactos[condacto[0]] = [None, None]
        datosCondacto = (codigo, condacto[1])
        if condacto[4] == 3:  # El condacto es igual en ambas versiones
          datosCondactos[condacto[0]] = (datosCondacto, datosCondacto)
        else:
          datosCondactos[condacto[0]][condacto[4] - 1] = datosCondacto
    # Cargamos las tablas de proceso
    numProceso = 0
    version    = 0  # Versi�n de DAAD necesaria, 0 significa compatibilidad con ambas
    for seccion in arbolSCE.find_data ('pro'):
      entero = seccion.children[0]
      numero = int (entero)
      if numero != numProceso:
        raise TabError ('n�mero de proceso %d en lugar de %d', (numProceso, numero), entero)
      cabeceras = []
      entradas  = []
      for procentry in seccion.find_data ('procentry'):
        palabras = []
        for word in procentry.find_data ('word'):
          palabra = str (word.children[0]).lower() if word.children else '_'
          palabras.append (palabra)
          if len (palabras) == 1 and palabra not in verbos:
            break  # Para conservar la posici�n de la primera palabra inexistente
        if palabras[0] not in verbos or palabras[1] not in nombres:
          raise TabError ('una palabra de vocabulario de tipo %s', 'nombre' if len (palabras) > 1 else 'verbo', word.meta)
        cabeceras.append ((verbos[palabras[0]], nombres[palabras[1]]))
        entrada = []
        for condacto in procentry.find_data ('condact'):
          for condactname in condacto.find_data ('condactname'):
            nombre = str (condactname.children[0])
          if nombre not in datosCondactos:
            raise TabError ('Condacto de nombre %s inexistente', nombre, condacto.meta)
          parametros = []
          for param in condacto.find_data ('param'):
            parametro = param.children[0]
            if parametro.type == 'INT':
              parametros.append (int (parametro))
            else:  # Valor no num�rico (p.ej. CARRIED)
              parametros.append (IDS_LOCS[str (parametro)])
          # Detectamos incompatibilidades por requerirse versiones de DAAD diferentes
          versionAntes = version
          if version:
            if not datosCondactos[nombre][version - 1]:
              raise TabError ('Condacto de nombre %s inexistente en DAAD versi�n %d (asumida por condactos anteriores)', (nombre, version), condacto.meta)
            # La comprobaci�n del n�mero de par�metros se hace abajo
            entrada.append ((datosCondactos[nombre][version - 1][0], parametros))
          else:
            # Fijamos versi�n de DAAD si el condacto con ese nombre s�lo est� en una
            if not datosCondactos[nombre][0] or not datosCondactos[nombre][1]:
              version = 1 if datosCondactos[nombre][0] else 2
              if version == 2:
                nueva_version.append (True)
            elif len (parametros) != len (datosCondactos[nombre][0][1]) and len (parametros) != len (datosCondactos[nombre][1][1]):
              if len (datosCondactos[nombre][0][1]) == len (datosCondactos[nombre][1][1]):
                requerido = len (datosCondactos[nombre][0][1])
              else:
                requerido = ' o '.join (sorted ((len (datosCondactos[nombre][0][1]), len (datosCondactos[nombre][1][1]))))
              raise TabError ('El condacto %s requiere %d par�metro%s', (nombre, requerido, '' if requerido == 1 else 's'), condacto.meta)
            # Fijamos versi�n de DAAD si el condacto con ese n�mero de par�metros s�lo est� en una
            elif len (datosCondactos[nombre][0][1]) != len (datosCondactos[nombre][1][1]):
              version = 1 if len (parametros) == len (datosCondactos[nombre][0][1]) else 2
              if version == 2:
                nueva_version.append (True)
            entrada.append ((datosCondactos[nombre][0][0], parametros))
            # TODO: poner a condactos anteriores con c�digo diferente entre versiones, el de la versi�n 2
            if version == 2:
              pass
          # Comprobamos el n�mero de par�metros
          if version and len (parametros) != len (datosCondactos[nombre][version - 1][1]):
            requerido = len (datosCondactos[nombre][version - 1][1])
            raise TabError ('El condacto %s requiere %d par�metro%s en DAAD versi�n %d (asumida por %s)', (nombre, requerido, '' if requerido == 1 else 's', version, 'condactos anteriores' if version == versionAntes else ('este mismo condacto, que s�lo existe en la versi�n ' + str (version))), condacto.meta)
        entradas.append (entrada)
      tablas_proceso.append ((cabeceras, entradas))
      numProceso += 1
    return
  except (TabError, lark.UnexpectedInput) as e:
    if type (e) == TabError:
      descripcion   = e.args[0]
      paramsFormato = e.args[1]
      if descripcion[0].islower():
        descripcion = 'Se esperaba ' + descripcion
      if len (e.args) > 2:
        posicion     = e.args[2]
        descripcion += ', en l�nea %d'
        if type (paramsFormato) == tuple:
          paramsFormato += (posicion.line, )
        else:
          paramsFormato = (paramsFormato, posicion.line)
        if len (e.args) == 3:
          descripcion   += ' columna %d'
          paramsFormato += (posicion.column, )
      texto = descripcion % paramsFormato
    else:
      texto = e
    prn ('Formato del c�digo fuente inv�lido o no soportado:', texto, file = sys.stderr, sep = '\n')
  except:
    pass
  return False

def carga_xmessage (desplazamiento):
  """Carga desde los ficheros de XMessages el mensaje que inicia en el desplazamiento dado, devolviendo None en caso de no lograrlo"""
  global ficherosXMessages, longFichXMessages
  try:
    ficherosXMessages
  except:
    ficherosXMessages = {}  # Ficheros de XMessages abiertos
    longFichXMessages = longitud_XMessages[plataforma] if plataforma in longitud_XMessages else longitud_XMessages[None]
  numFichero = desplazamiento // longFichXMessages
  if numFichero in ficherosXMessages:
    fichero = ficherosXMessages[numFichero]
  else:
    fichero = abreFichXMessages (numFichero)
    if fichero == None:
      return None
    ficherosXMessages[numFichero] = fichero
  fichero.seek (desplazamiento % longFichXMessages)
  return cargaCadena (fichero)

def escribe_secs_ctrl (cadena):
  """Devuelve la cadena dada convirtiendo la representaci�n de secuencias de control en sus c�digos"""
  # TODO: implementar
  return cadena

def inicializa_banderas (banderas):
  """Inicializa banderas con valores propios de DAAD"""
  # Banderas 0-28:
  # Comprobado con el int�rprete DAAD de la versi�n EGA de Jabato, y el de Chichen Itz�:
  # Se inicializan todas a 0

  # Bandera 29:
  # Es posible que el bit 7 signifique que tenemos un modo gr�fico (320x200),
  # con 53 columnas, en lugar de 80 (modo texto)
  # Comprobado con el int�rprete DAAD de la versi�n EGA de Jabato:
  # - Con EGA-SVGA, se inicializa a 128
  # - Con Hercules, se inicializa a 0
  # Con el int�rprete DAAD de Chichen Itz�, se inicializa al menos en alg�n modo gr�fico, a 129
  if nueva_version:
    banderas[29] = 129
  else:
    banderas[29] = 128

  # Banderas 30-36:
  # Comprobado con el int�rprete DAAD de la versi�n EGA de Jabato, y el de Chichen Itz�:
  # Se inicializan todas a 0

  # Bandera 37:
  # Comprobado con el int�rprete DAAD de la versi�n EGA de Jabato: se inicializa a 4
  # Con el int�rprete DAAD de Chichen Itz�: Se inicializa a 0
  if nueva_version:
    banderas[37] = 0

  # Bandera 38:
  # Comprobado con el int�rprete DAAD de la versi�n EGA de Jabato, y el de Chichen Itz�:
  # Se inicializa a 0

  # Bandera 39:
  # En el int�rprete DAAD de la Aventura Original: Se inicializa a 4
  # En el int�rprete DAAD de la versi�n EGA de Jabato: Se inicializa a 13
  # En el int�rprete DAAD de Chichen Itz�: Se inicializa a 0
  if not nueva_version:
    banderas[39] = 13

  # Banderas 40-45:
  # Comprobado con el int�rprete DAAD de la versi�n EGA de Jabato, y el de Chichen Itz�:
  # Se inicializan todas a 0

  # Banderas 46 y 47:
  # Comprobado con el int�rprete DAAD de la versi�n EGA de Jabato:
  # Se inicializan a 255
  # Con el int�rprete DAAD de Chichen Itz�: Se inicializa a 0
  if nueva_version:
    banderas[46] = 0
    banderas[47] = 0

  # Banderas 48-51:
  # Comprobado con el int�rprete DAAD de la versi�n EGA de Jabato, y el de Chichen Itz�:
  # Se inicializan todas a 0

  # Bandera 52:
  # Comprobado con el int�rprete DAAD de la versi�n EGA de Jabato: Se inicializa a 10
  # Con el int�rprete DAAD de Chichen Itz�: Se inicializa a 0
  if nueva_version:
    banderas[52] = 0

  # Banderas 53-61:
  # Comprobado con el int�rprete DAAD de la versi�n EGA de Jabato, y el de Chichen Itz�:
  # Se inicializan todas a 0

  # Bandera 62:
  # Comprobado con el int�rprete DAAD de la versi�n EGA de Jabato: Se inicializa a 0
  # Con el int�rprete DAAD de Chichen Itz�: Se inicializa a 13 en EGA, y 141 en VGA
  if nueva_version:
    banderas[62] = 13

  # Banderas 63-254:
  # Comprobado con el int�rprete DAAD de la versi�n EGA de Jabato, y el de Chichen Itz�:
  # Se inicializan todas a 0

def lee_secs_ctrl (cadena):
  """Devuelve la cadena dada convirtiendo las secuencias de control en una representaci�n imprimible. Usa la nomenclatura est�ndar del manual de DAAD"""
  if nueva_version:
    cadena = cadena.replace ('\x0b', '\\b').replace ('\x0c', '\\k')
  return cadena.replace ('\\', '\\\\').replace ('\n', '\\n')

def nueva_bd ():
  """Crea una nueva base de datos de DAAD"""
  pass  # TODO: Por implementar


# Funciones de apoyo de bajo nivel

def cargaCadena (fichero):
  """Carga una cadena desde el fichero dado y la devuelve"""
  cadena = []
  while True:
    caracter = ord (fichero.read (1)) ^ 255
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
    elif caracter == ord ('\r'):  # Un car�cter de nueva l�nea en la cadena
      cadena.append ('\n')
    elif (caracter < 16) or (caracter > 31):
      cadena.append (chr (caracter))
    else:
      cadena.append (daad_a_chr[caracter - 16])
  return ''.join (cadena)

def guardaCadena (cadena):
  """Guarda una cadena sin abreviar, en el formato de DAAD"""
  cuenta = 0
  for caracter in cadena:
    if ord (caracter) > 127:  # Conversi�n necesaria
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
    prn ('Error en guardaCadena: la cadena "%s" tiene %d caracteres que exceden el c�digo 127, pero no salen en daad_a_chr' %
        (cadena, cuenta))

def guardaCadenaAbreviada (cadena):
  """Guarda una cadena abreviada, en el formato de DAAD"""
  for caracter in cadena:
    caracter = ord (caracter)
    guarda_int1 (caracter ^ 255)
  guarda_int1 (ord ('\n') ^ 255)  # Fin de cadena


# Funciones de apoyo de alto nivel

def abreFichXMessages (numFichero):
  """Abre el fichero de XMessages de n�mero dado busc�ndolo en la ruta de la base de datos actual, devolviendo None en caso de no lograrlo"""
  nombreFich = str (numFichero) + '.xmb'
  # Buscamos el fichero con independencia de may�sculas y min�sculas
  for nombreFichero in os.listdir (os.path.dirname (ruta_bbdd)):
    if nombreFichero.lower() == nombreFich:
      nombreFich = nombreFichero
      break
  else:
    prn ('No se encuentra el fichero de XMessages de Maluva', str (numFichero) + '.XMB', file = sys.stderr)
    return None
  try:
    fichero = open (os.path.join (os.path.dirname (ruta_bbdd), nombreFich), 'rb')
  except:
    prn ('No se puede abrir el fichero de XMessages de Maluva', nombreFich, file = sys.stderr)
    return None
  return fichero

def abreviaCadenas ():
  """Abrevia las distintas cadenas abreviables"""
  global desc_locs_abrev, desc_objs_abrev, msgs_sys_abrev, msgs_usr_abrev
  desc_locs_abrev = []
  desc_objs_abrev = []
  msgs_sys_abrev  = []
  msgs_usr_abrev  = []
  if not abreviaturas:
    return
  for cadena in desc_locs:
    desc_locs_abrev.append (daCadenaAbreviada (cadena))
  if compatibilidad:
    for cadena in desc_objs:  # DC no los abrevia, porque no funciona bien en el int�rprete
      desc_objs_abrev.append (cadena)
  else:
    for cadena in desc_objs:
      # XXX: �lista mal los objetos si se abrevian, al menos en la AO de PC (hace mal la conversi�n de su art�culo)?
      desc_objs_abrev.append (daCadenaAbreviada (cadena))
  for cadena in msgs_sys:
    # FIXME: parece mostrar mal alguno de ellos si se abrevian, al menos en la AO de PC
    # tal vez abrevie mal
    msgs_sys_abrev.append (daCadenaAbreviada (cadena))
  for cadena in msgs_usr:
    msgs_usr_abrev.append (daCadenaAbreviada (cadena))

def calcula_abreviaturas (maxAbrev):
  """Calcula y devuelve las abreviaturas �ptimas, y la longitud de las cadenas tras aplicarse

  maxAbrev es la longitud m�xima de las abreviaturas"""
  global longAntes  # Longitud total de las cadenas antes de aplicar abreviaturas
  try:
    longAntes = longAntes
  except:
    longAntes = 0
  # prn (desc_locs)
  cadenas     = []  # Cadenas sobre las que aplicar abreviaturas
  longDespues = 0   # Longitud total de las cadenas tras aplicar abreviaturas, incluyendo espacio de �stas
  minAbrev    = 2   # Longitud m�nima de las abreviaturas
  if compatibilidad:
    listasCadenas = (desc_locs, msgs_sys, msgs_usr)
  else:
    listasCadenas = (desc_locs, desc_objs, msgs_sys, msgs_usr)
  if not longAntes:
    for listaCadenas in listasCadenas:
      for cadena in listaCadenas:
        longCadena  = len (cadena) + 1
        longAntes  += longCadena
        cadenas.append (cadena)
    if compatibilidad:
      prn ('Longitud de cadenas sin abreviar (excluyendo objetos):', longAntes)
    else:
      prn ('Longitud de cadenas sin abreviar:', longAntes)
  else:
    for listaCadenas in listasCadenas:
      for cadena in listaCadenas:
        cadenas.append (cadena)
  # Tomamos las mejores abreviaturas
  num_abreviaturas = 128 if compatibilidad else 129
  optimas = []  # Abreviaturas �ptimas calculadas
  for i in range (num_abreviaturas):
    # Calculamos cu�ntas veces aparece cada combinaci�n
    ahorros     = {}  # Cu�ntos bytes en total se ahorrar�an por abreviar cada ocurrencia
    ocurrencias = {}  # Cu�ntas veces aparece cada combinaci�n de caracteres
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
    if not ahorros:  # Ya no hay m�s cadenas de longitud m�nima
      break
    ordenAhorro = sorted (ahorros, key = ahorros.get, reverse = True)
    abreviatura = ordenAhorro[0]
    ahorro      = ahorros[abreviatura]
    # prn ((abreviatura, ahorro, ocurrencias[abreviatura]))
    # Buscamos superconjuntos entre el resto de combinaciones posibles
    maxAhorroSup = ahorro  # Ahorro m�ximo combinado por reemplazar abreviatura por un superconjunto, entre ambos
    maxSuperCjto = None
    posMaxAhorro = None
    sconjto      = None
    if i < 100:  # En las �ltimas, es poco probable que se aproveche esto
      for d in range (1, len (ordenAhorro)):  # Buscamos superconjuntos entre el resto de combinaciones posibles
        if abreviatura in ordenAhorro[d]:
          sconjto   = ordenAhorro[d]
          ahorroSup = ahorros[sconjto] + ((ocurrencias[abreviatura] - ocurrencias[sconjto]) * (len (abreviatura) - 1))
          if ahorroSup > maxAhorroSup:
            maxAhorroSup = ahorroSup
            maxSuperCjto = sconjto
            posMaxAhorro = d
            # prn ('"%s" (%d) es superconjunto de "%s", ahorros %d, ocurrencias %d. Ahorros combinados tomando �ste %d' %
            #     (sconjto, d, abreviatura, ahorros[sconjto], ocurrencias[sconjto], ahorroSup))
    if posMaxAhorro:  # Ten�a alg�n superconjunto (TODO: puede que siempre ocurra, si len (abreviatura) < maxAbrev)
      # prn ('La entrada "' + ordenAhorro[posMaxAhorro] + '" (' + str(posMaxAhorro) + ') reemplaza "' + abreviatura + '" (0)')
      abreviatura = maxSuperCjto
    # A�adimos esta abreviatura a la lista de abreviaturas �ptimas calculadas
    ahorro = ahorros[abreviatura]
    if ahorro < 0:  # Ahorra m�s con 0 que con 1, seguramente por los superconjuntos
      break  # Ya no se ahorra nada m�s
    # prn ((abreviatura, ahorro, ocurrencias[abreviatura]))
    optimas.append ((abreviatura, ahorro, ocurrencias[abreviatura]))
    longDespues += len (abreviatura)
    # Quitamos las ocurrencias de esta abreviatura en las cadenas
    c = 0
    nuevasCadenas = []
    while c < len (cadenas):
      partes = cadenas[c].split (abreviatura)
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
    longDespues += num_abreviaturas - len (optimas)  # Se reemplazar�n por abreviaturas de un byte
  prn ('Con longitud m\xc3\xa1xima de las abreviaturas %d, longitud de cadenas tras abreviar: %d.' % (maxAbrev, longDespues))
  prn (optimas)
  nuevasAbreviaturas = []
  for abreviatura in optimas:
    nuevasAbreviaturas.append (abreviatura[0])
  return (nuevasAbreviaturas, longDespues)

def cargaAbreviaturas ():
  """Carga las abreviaturas"""
  global abreviaturas
  abreviaturas = []
  # Vamos a la posici�n de las abreviaturas
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

def cargaAtributos ():
  """Carga los atributos de los objetos"""
  # Cargamos el n�mero de objetos (no lo tenemos todav�a)
  fich_ent.seek (CAB_NUM_OBJS)
  num_objetos[0] = carga_int1()
  # Vamos a la posici�n de los atributos de los objetos
  fich_ent.seek (carga_desplazamiento (CAB_POS_ATRIBS_OBJS))
  # Cargamos los atributos de cada objeto
  for i in range (num_objetos[0]):
    atributos.append (carga_int1())

def cargaAtributosExtra ():
  """Carga los atributos extra de los objetos"""
  # Vamos a la posici�n de los atributos de los objetos
  fich_ent.seek (carga_desplazamiento (CAB_POS_ATRIBS_EXTRA_OBJS))
  # Cargamos los atributos de cada objeto
  for i in range (num_objetos[0]):
    atributos_extra.append (carga_int2())  # FIXME: averiguar si su "endianismo" es fijo

def cargaCadenas (pos_num_cads, pos_lista_pos, cadenas):
  """Carga un conjunto gen�rico de cadenas

  pos_num_cads es la posici�n de donde obtener el n�mero de cadenas
  pos_lista_pos posici�n de donde obtener la lista de posiciones de las cadenas
  cadenas es la lista donde almacenar las cadenas que se carguen"""
  # Cargamos el n�mero de cadenas
  fich_ent.seek (pos_num_cads)
  num_cads = carga_int1()
  # Vamos a la posici�n de la lista de posiciones de cadenas
  fich_ent.seek (carga_desplazamiento (pos_lista_pos))
  # Cargamos las posiciones de las cadenas
  posiciones = []
  for i in range (num_cads):
    posiciones.append (carga_desplazamiento())
  # Cargamos cada cadena
  for posicion in posiciones:
    fich_ent.seek (posicion)
    cadenas.append (cargaCadena (fich_ent))

def cargaConexiones ():
  """Carga las conexiones entre localidades"""
  # Cargamos el n�mero de localidades
  fich_ent.seek (CAB_NUM_LOCS)
  num_locs = carga_int1()
  # Vamos a la posici�n de la lista de posiciones de las conexiones
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
      verbo = carga_int1()  # Verbo de direcci�n
      if verbo == 255:  # Fin de las conexiones de esta localidad
        break
      destino = carga_int1()  # Localidad de destino
      salidas.append ((verbo, destino))
    conexiones.append (salidas)

def cargaLocalidadesObjetos ():
  """Carga las localidades iniciales de los objetos (d�nde est� cada uno)"""
  # Vamos a la posici�n de las localidades de los objetos
  fich_ent.seek (carga_desplazamiento (CAB_POS_LOCS_OBJS))
  # Cargamos la localidad de cada objeto
  for i in range (num_objetos[0]):
    locs_iniciales.append (carga_int1())

def cargaNombresObjetos ():
  """Carga los nombres y adjetivos de los objetos"""
  # Vamos a la posici�n de los nombres de los objetos
  fich_ent.seek (carga_desplazamiento (CAB_POS_NOMS_OBJS))
  # Cargamos el nombre y adjetivo de cada objeto
  for i in range (num_objetos[0]):
    nombres_objs.append ((carga_int1(), carga_int1()))

def cargaTablasProcesos ():
  """Carga las tablas de procesos"""
  # En PAWS:
  #   El proceso 0 es la tabla de respuestas
  #   En los procesos 1 y 2, las cabeceras de las entradas se ignoran, condicionalmente seg�n una bandera"""
  # Cargamos el n�mero de procesos
  fich_ent.seek (CAB_NUM_PROCS)
  num_procs = carga_int1()
  # prn (num_procs, 'procesos')
  # Vamos a la posici�n de la lista de posiciones de los procesos
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
        if condacto > 127:  # Condacto con indirecci�n
          num_condacto = condacto - 128
        else:
          num_condacto = condacto
        parametros = []
        if num_condacto not in condactos:
          try:
            muestraFallo ('FIXME: Condacto desconocido', 'C�digo de condacto: ' + str (num_condacto) + '\nProceso: ' + str (num_proceso) + '\n�ndice de entrada: ' + str (num_entrada))
          except:
            prn ('FIXME: N�mero de condacto', num_condacto, 'desconocido, en entrada', num_entrada, 'del proceso', num_proceso)
          return
        for i in range (len (condactos[num_condacto][1])):
          parametros.append (carga_int1())
        if plataforma not in (5, 6) and num_condacto == 61 and parametros[1] == 3:  # XMES de Maluva
          parametros.append (carga_int1())
        entrada.append ((condacto, parametros))
      entradas.append (entrada)
    if len (cabeceras) != len (entradas):
      prn ('ERROR: N�mero distinto de cabeceras y entradas para una tabla de',
           'procesos')
      return
    tablas_proceso.append ((cabeceras, entradas))

def cargaVocabulario ():
  """Carga el vocabulario"""
  # Vamos a la posici�n del vocabulario
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
    # DAAD guarda las palabras en may�sculas, salvo las tildes (en min�scula)
    vocabulario.append ((''.join (palabra).rstrip().lower(), carga_int1(),
                         carga_int1()))

def daCadenaAbreviada (cadena):
  """Devuelve una cadena abreviada, aplic�ndole las abreviaturas"""
  if not abreviaturas:
    return cadena
  # Realizamos los reemplazos de las abreviaturas, por orden de aparici�n de �stas
  partesCadena = [cadena]
  for a in range (len (abreviaturas)):
    abreviatura = abreviaturas[a]
    i = 0
    while i < len (partesCadena):
      parteCadena = partesCadena[i]
      if type (parteCadena) != str:
        i += 1
        continue
      partes = parteCadena.split (abreviatura)
      if len (partes) > 1:
        partesCadena[i] = partes[0]
        for p in range (1, len (partes)):
          partesCadena.insert (i + ((p - 1) * 2) + 1, (a, ))  # Guardamos el c�digo de abreviatura en una tupla
          partesCadena.insert (i + ((p - 1) * 2) + 2, partes[p])
        i += p * 2
      i += 1
  # Juntamos todas las partes en una sola cadena abreviada
  abreviada = ''  # Forma abreviada de la cadena
  cuenta    = 0   # Caract�res inv�lidos, no deber�a ocurrir
  for parteCadena in partesCadena:
    if type (parteCadena) != str:
      abreviada += chr (127 + parteCadena[0])
      continue
    if not parteCadena:  # Cadena vac�a
      continue
    for caracter in parteCadena:
      if ord (caracter) > 127:  # Conversi�n necesaria
        try:
          caracter = chr (daad_a_chr.index (caracter) + 16)
        except:
          cuenta += 1
      elif caracter == '\n':
        caracter = '\r'
      abreviada += caracter
  if cuenta:
    prn ('Error en daCadenaAbreviada: la cadena "%s" tiene %d caracteres que exceden el c�digo 127, pero no salen en daad_a_chr' %
        (cadena, cuenta))
  return abreviada

def guardaAbreviaturas ():
  """Guarda la secci�n de abreviaturas sobre el fichero de salida, en caso de tenerlas, y devuelve cu�ntos bytes ocupa la secci�n"""
  if abreviaturas:  # Si hay abreviaturas...
    ocupado = 0
    for indice_abrev in range (129):  # ... habr� 129
      if indice_abrev >= len (abreviaturas):
        # TODO: sin modo compatibilidad no servir� esta
        abreviatura = chr (127)  # Abreviatura de relleno (una ya existente, de un byte)
      else:
        abreviatura = abreviaturas[indice_abrev]
      for pos in range (len (abreviatura)):
        caracter = abreviatura[pos]
        if ord (caracter) > 127:  # Conversi�n necesaria
          caracter = daad_a_chr.index (caracter) + 16
        else:
          caracter = ord (caracter)
        if pos == (len (abreviatura) - 1):
          caracter += 128
        guarda_int1 (caracter)
      ocupado += len (abreviatura)
    return ocupado
  return 0

def guarda_bd_ (bbdd):
  """Almacena la base de datos entera en el fichero de salida, por orden de conveniencia, pero con vocabulario primero"""
  # TODO: poner paddings
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
  abreviaCadenas()
  fich_sal     = bbdd
  num_locs     = len (desc_locs)       # N�mero de localidades
  num_msgs_usr = len (msgs_usr)        # N�mero de mensajes de usuario
  num_msgs_sys = len (msgs_sys)        # N�mero de mensajes de sistema
  num_procs    = len (tablas_proceso)  # N�mero de tablas de proceso
  bajo_nivel_cambia_sal (bbdd)
  guarda_int1 (1)             # Versi�n del formato
  guarda_int1 (plataforma)    # Identificador de plataforma
  guarda_int1 (95)            # No s� qu� es, pero vale esto en las BBDD DAAD
  guarda_int1 (num_objetos[0])
  guarda_int1 (num_locs)
  guarda_int1 (num_msgs_usr)
  guarda_int1 (num_msgs_sys)
  guarda_int1 (num_procs)
  ocupado = 32  # Espacio ocupado hasta ahora (incluyendo la cabecera)
  # Reservamos espacio para el vocabulario
  pos_vocabulario = ocupado
  ocupado += (7 * len (vocabulario)) + 1
  # Posici�n de las abreviaturas
  if abreviaturas:
    guarda_desplazamiento (ocupado)
    for abreviatura in abreviaturas:
      ocupado += len (abreviatura)
  else:
    guarda_int2 (0)  # Sin abreviaturas
  # Posici�n de la lista de posiciones de los procesos
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_procs
  # Posici�n de la lista de posiciones de las descripciones de los objetos
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_objetos[0]
  # Posici�n de la lista de posiciones de las descripciones de las localidades
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_locs
  # Posici�n de la lista de posiciones de los mensajes de usuario
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_msgs_usr
  # Posici�n de la lista de posiciones de los mensajes de sistema
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_msgs_sys
  # Posici�n de la lista de posiciones de las conexiones
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_locs
  # Posici�n del vocabulario
  guarda_desplazamiento (pos_vocabulario)
  # Posici�n de las localidades de los objetos
  guarda_desplazamiento (ocupado)
  ocupado += num_objetos[0] + 1
  # Posici�n de los nombres de los objetos
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_objetos[0]
  # Posici�n de los atributos de los objetos
  guarda_desplazamiento (ocupado)
  ocupado += num_objetos[0]
  # Longitud del fichero
  guarda_int2 (0)  # Luego guardaremos el valor correcto (a�n no lo sabemos)
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
  ocupado += guardaPosDescObjs (ocupado)
  # Guardamos las posiciones de las descripciones de las localidades
  ocupado += guardaPosDescLocs (ocupado)
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
    guarda_int2 (0)  # Fin del proceso (no tiene m�s entradas)
  # Guardamos las descripciones de los objetos
  guardaDescObjs()
  # Guardamos las descripciones de las localidades
  guardaDescLocs()
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
      longMin = longAbrev  # Reducci�n m�xima de longitud total de textos lograda
      longMax = maxAbrev   # Longitud m�xima en la b�squeda de abreviaturas
  if longMin < longAntes:
    prn (longAntes - longMin, 'bytes ahorrados por abreviaci�n de textos')
    prn ('La mejor combinaci�n de abreviaturas se encontr� con longitud m�xima de abreviatura', longMax)
    prn (len (abreviaturas), 'abreviaturas en total, que son:')
    prn (abreviaturas)
  else:
    prn ('No se ahorra nada por abreviaci�n de textos, abreviaturas desactivadas')
    abreviaturas = []
  abreviaCadenas()
  fich_sal     = bbdd
  num_locs     = len (desc_locs)       # N�mero de localidades
  num_msgs_usr = len (msgs_usr)        # N�mero de mensajes de usuario
  num_msgs_sys = len (msgs_sys)        # N�mero de mensajes de sistema
  num_procs    = len (tablas_proceso)  # N�mero de tablas de proceso
  bajo_nivel_cambia_sal (bbdd)
  guarda_int1 (version)         # Versi�n del formato
  guarda_int1 (plataforma + 1)  # Identificador de plataforma e idioma
  guarda_int1 (ord ('_'))       # Car�cter para representar cualquier palabra, vale esto en las BBDD DAAD de AD
  guarda_int1 (num_objetos[0])
  guarda_int1 (num_locs)
  guarda_int1 (num_msgs_usr)
  guarda_int1 (num_msgs_sys)
  guarda_int1 (num_procs)
  ocupado = 32  # Espacio ocupado hasta ahora (incluyendo la cabecera)
  if version > 1:
    ocupado += 2
  # Posici�n de las abreviaturas
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
  # Posici�n de la lista de posiciones de los procesos
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_procs
  # Posici�n de la lista de posiciones de las descripciones de los objetos
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_objetos[0]
  # Posici�n de la lista de posiciones de las descripciones de las localidades
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_locs
  # Posici�n de la lista de posiciones de los mensajes de usuario
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_msgs_usr
  # Posici�n de la lista de posiciones de los mensajes de sistema
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_msgs_sys
  # Posici�n de la lista de posiciones de las conexiones
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_locs
  # Posici�n del vocabulario
  guarda_desplazamiento (ocupado)
  ocupado += (7 * len (vocabulario)) + 1
  # Posici�n de las localidades de los objetos
  guarda_desplazamiento (ocupado)
  ocupado += num_objetos[0] + 1
  # Posici�n de los nombres de los objetos
  guarda_desplazamiento (ocupado)
  ocupado += 2 * num_objetos[0]
  # Posici�n de los atributos de los objetos
  guarda_desplazamiento (ocupado)
  ocupado += num_objetos[0]
  # Posici�n de los atributos extra de los objetos
  if version > 1:
    guarda_desplazamiento (ocupado)
    ocupado += 2 * num_objetos[0]
  # Longitud del fichero
  guarda_int2 (0)  # Luego guardaremos el valor correcto (a�n no lo sabemos)
  # Fin de la cabecera

  # Guardamos las abreviaturas (si las hay)
  guardaAbreviaturas()
  # A�adimos padding condicional para las plataformas que lo requieran
  if paddingTrasAbrev:
    guarda_int1 (0)  # Relleno (padding)
  # Guardamos las posiciones de las cabeceras de las tablas de proceso
  for tabla in tablas_proceso:
    guarda_desplazamiento (ocupado)
    ocupado += (4 * len (tabla[0])) + 2
  # Guardamos las posiciones de las descripciones de los objetos
  ocupado += guardaPosDescObjs (ocupado)
  # Guardamos las posiciones de las descripciones de las localidades
  ocupado += guardaPosDescLocs (ocupado)
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
        if entradaProceso == entradas[i]:  # Ya hab�a un bloque de proceso igual
          guarda_desplazamiento (desplazamiento)
          try:
            for condacto, parametros in entradas[i]:
              ahorroProcesos += 1 + len (parametros)
          except:
            # prn (entradas[i])  # Ya se habr� hecho esto la primera vez
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
    guarda_int2 (0)  # Fin del proceso (no tiene m�s entradas)
  prn (ahorroProcesos, 'bytes ahorrados por deduplicar bloques de proceso')
  # Guardamos las descripciones de los objetos
  guardaDescObjs()
  # Guardamos las descripciones de las localidades
  guardaDescLocs()
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
      entradasProceso.append (entrada)
      for condacto, parametros in entrada:
        guarda_int1 (condacto)
        for parametro in parametros:
          guarda_int1 (parametro)
      guarda_int1 (255)  # Fin de la entrada
  # Guardamos la longitud final del fichero
  fich_sal.seek (CAB_LONG_FICH)
  guarda_desplazamiento (ocupado)

def guardaDescLocs (posInicial = 0):
  """Guarda la secci�n de descripciones de las localidades sobre el fichero de salida, y devuelve cu�ntos bytes ocupa la secci�n, y las posiciones de cada descripci�n incluyendo posInicial"""
  return guardaMsgs (desc_locs, desc_locs_abrev, posInicial)

def guardaDescObjs (posInicial = 0):
  """Guarda la secci�n de descripciones de los objetos sobre el fichero de salida, y devuelve cu�ntos bytes ocupa la secci�n, y las posiciones de cada descripci�n incluyendo posInicial"""
  return guardaMsgs (desc_objs, desc_objs_abrev, posInicial)

def guardaMsgs (msgs, msgsAbrev, posInicial = 0):
  """Guarda una secci�n de mensajes sobre el fichero de salida, y devuelve cu�ntos bytes ocupa la secci�n, y las posiciones de cada mensaje incluyendo posInicial"""
  ocupado    = 0
  posiciones = []
  if abreviaturas and msgsAbrev:
    for mensaje in msgsAbrev:
      posiciones.append (posInicial + ocupado)
      guardaCadenaAbreviada (mensaje)
      ocupado += len (mensaje) + 1
  else:
    for mensaje in msgs:
      posiciones.append (posInicial + ocupado)
      guardaCadena (mensaje)
      ocupado += len (mensaje) + 1
  return ocupado, posiciones

def guardaMsgsSys (posInicial = 0):
  """Guarda la secci�n de mensajes de sistema sobre el fichero de salida, y devuelve cu�ntos bytes ocupa la secci�n, y las posiciones de cada mensaje incluyendo posInicial"""
  return guardaMsgs (msgs_sys, msgs_sys_abrev, posInicial)

def guardaMsgsUsr (posInicial = 0):
  """Guarda la secci�n de mensajes de usuario sobre el fichero de salida, y devuelve cu�ntos bytes ocupa la secci�n, y las posiciones de cada mensaje incluyendo posInicial"""
  return guardaMsgs (msgs_usr, msgs_usr_abrev, posInicial)

def guardaPosDescLocs (pos):
  """Guarda la secci�n de posiciones de las descripciones de localidades sobre el fichero de salida, y seg�n el tipo del par�metro, devuelve cu�ntos bytes ocupa la secci�n o cu�ntos ocupan las descripciones

  pos es la posici�n donde se guardar� la primera descripci�n, o bien una lista con la posici�n de cada descripci�n. Si es el primer caso, la funci�n devuelve cu�nto ocupan las descripciones, y en el segundo caso, devuelve cu�nto ocupa la secci�n"""
  return guardaPosMsgs (desc_locs, desc_locs_abrev, pos)

def guardaPosDescObjs (pos):
  """Guarda la secci�n de posiciones de las descripciones de objetos sobre el fichero de salida, y seg�n el tipo del par�metro, devuelve cu�ntos bytes ocupa la secci�n o cu�ntos ocupan las descripciones

  pos es la posici�n donde se guardar� la primera descripci�n, o bien una lista con la posici�n de cada descripci�n. Si es el primer caso, la funci�n devuelve cu�nto ocupan las descripciones, y en el segundo caso, devuelve cu�nto ocupa la secci�n"""
  return guardaPosMsgs (desc_objs, desc_objs_abrev, pos)

def guardaPosMsgs (msgs, msgsAbrev, pos):
  """Guarda una secci�n de posiciones de mensajes sobre el fichero de salida, y seg�n el tipo del par�metro, devuelve cu�ntos bytes ocupa la secci�n o cu�ntos ocupan los mensajes

  pos es la posici�n donde se guardar� el primer mensaje, o bien una lista con la posici�n de cada mensaje. Si es el primer caso, la funci�n devuelve cu�nto ocupan los mensajes, y en el segundo caso, devuelve cu�nto ocupa la secci�n"""
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
  """Guarda la secci�n de posiciones de los mensajes de sistema sobre el fichero de salida, y seg�n el tipo del par�metro, devuelve cu�ntos bytes ocupa la secci�n o cu�ntos ocupan los mensajes

  pos es la posici�n donde se guardar� el primer mensaje, o bien una lista con la posici�n de cada mensaje. Si es el primer caso, la funci�n devuelve cu�nto ocupan los mensajes, y en el segundo caso, devuelve cu�nto ocupa la secci�n"""
  return guardaPosMsgs (msgs_sys, msgs_sys_abrev, pos)

def guardaPosMsgsUsr (pos):
  """Guarda la secci�n de posiciones de los mensajes de sistema sobre el fichero de salida, y seg�n el tipo del par�metro, devuelve cu�ntos bytes ocupa la secci�n o cu�ntos ocupan los mensajes

  pos es la posici�n donde se guardar� el primer mensaje, o bien una lista con la posici�n de cada mensaje. Si es el primer caso, la funci�n devuelve cu�nto ocupan los mensajes, y en el segundo caso, devuelve cu�nto ocupa la secci�n"""
  return guardaPosMsgs (msgs_usr, msgs_usr_abrev, pos)

def guardaVocabulario ():
  """Guarda la secci�n de vocabulario sobre el fichero de salida, y devuelve cu�ntos bytes ocupa la secci�n"""
  for palabra in vocabulario:
    # Rellenamos el texto de la palabra con espacios al final
    cadena = palabra[0].ljust (LONGITUD_PAL)
    for caracter in cadena:
      if ord (caracter) > 127:  # Conversi�n necesaria
        caracter = daad_a_chr.index (caracter) + 16
      else:
        caracter = ord (caracter.upper())
      guarda_int1 (caracter ^ 255)
    guarda_int1 (palabra[1])  # C�digo de la palabra
    guarda_int1 (palabra[2])  # Tipo de la palabra
  guarda_int1 (0)  # Fin del vocabulario
  return (len (vocabulario) * (LONGITUD_PAL + 2)) + 1

def preparaPlataforma ():
  """Prepara la configuraci�n sobre la plataforma"""
  global alinear, carga_int2, despl_ini, guarda_int2, plataforma, tam_cabecera, version, CAB_LONG_FICH
  # Cargamos la versi�n del formato de base de datos
  fich_ent.seek (CAB_VERSION)
  version = carga_int1()
  if version > 1:
    CAB_LONG_FICH += 2
    condactos.update (condactos_nuevos)
    nueva_version.append (True)
  else:
    NOMBRES_PROCS.extend(['Tabla de respuestas', 'Tras la descripci�n', 'Cada turno'])
  tam_cabecera = CAB_LONG_FICH + 2  # Longitud de la cabecera
  # Cargamos el identificador de plataforma
  fich_ent.seek (CAB_PLATAFORMA)
  plataforma = carga_int1() >> 4

  # Preparamos el desplazamiento inicial para carga desde memoria
  detectar_despl = False
  if plataforma in despl_ini_plat:
    despl_ini = despl_ini_plat[plataforma]
    if type (despl_ini) == list:
      detectar_despl = True
      despl_ini      = despl_ini[0]

  # Detectamos "endianismo"
  le = False
  if plataforma in plats_LE:
    le = True
  elif version > 1 and plataforma in plats_detectarLE:
    asumidoLE = False
    sePasan   = 0  # Desplazamientos en la cabecera que exceden longitud real del fichero de BD
    # Si el fichero de base de datos tiene tama�o correcto, esta heur�stica bastar�
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

  # Detectamos si hay 13 punteros de funciones externas, como ocurre en todas las aventuras de DAAD versi�n 2 menos las primeras
  fich_ent.seek (tam_cabecera)
  ceros = 0
  for i in range (13):
    if carga_int2() == 0:
      ceros += 1
  if ceros > 6:
    tam_cabecera += 26

  if detectar_despl:
    minimo = 999999
    fich_ent.seek (CAB_POS_ABREVS)
    for posCabecera in range (CAB_POS_ABREVS, tam_cabecera, 2):
      desplazamiento = carga_int2()
      if not desplazamiento:  # Puede tener 0 en abreviaturas y funciones externas
        continue
      if desplazamiento < minimo:
        minimo = desplazamiento
    despl_ini = minimo - tam_cabecera
    if tam_cabecera > 34 and ceros < 13:
      # Puede haber c�digo ensamblador entre la cabecera y donde apunta el primer puntero
      lista = []
      for reintentos in range (60):
        if validaPunteros (tam_cabecera):
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
  # Vamos a la posici�n de la lista de posiciones de los procesos
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

  # XXX: continuar la implementaci�n si fuera necesario, revisando m�s punteros
  return True
