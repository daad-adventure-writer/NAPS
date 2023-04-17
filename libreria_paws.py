# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Librería de PAWS (parte común a editor, compilador e intérprete)
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

import alto_nivel


# Variables que se exportan (fuera del paquete)

# Ponemos los módulos de condactos en orden, para permitir que las funciones de los condactos de igual firma (nombre, tipo y número de parámetros) de los sistemas más nuevos tengan precedencia sobre las de sistemas anteriores
mods_condactos = ('condactos_paws', 'condactos_quill')

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
funcs_importar = (
  ('carga_bd',     ('pdb',), 'Bases de datos PAWS'),
  ('carga_bd_sna', ('sna',), 'Imagen de memoria de ZX 48K con PAWS'),
  ('carga_sce',    ('sce',), 'Código fuente de PAWS'),
)
# Función que crea una nueva base de datos (vacía)
func_nueva = ''


# Constantes que se exportan (fuera del paquete)

EXT_SAVEGAME     = 'pgp'   # Extensión para las partidas guardadas
INDIRECCION      = False   # El parser no soporta indirección (para el IDE)
LONGITUD_PAL     = 5       # Longitud máxima para las palabras de vocabulario
NOMBRE_SISTEMA   = 'PAWS'  # Nombre de este sistema
NUM_ATRIBUTOS    = [8]     # Número de atributos de objeto
NUM_BANDERAS     = 256     # Número de banderas del parser
# Nombres de las primeras tablas de proceso (para el IDE)
NOMBRES_PROCS    = ('Tabla de respuestas', 'Tras la descripción', 'Cada turno')
# Nombres de los tipos de palabra (para el IDE)
TIPOS_PAL = ('Verbo', 'Adverbio', 'Nombre', 'Adjetivo', 'Preposicion', 'Conjuncion', 'Pronombre')


alinear          = False       # Si alineamos con relleno (padding) las listas de desplazamientos a posiciones pares
compatibilidad   = True        # Modo de compatibilidad con los intérpretes originales
conversion       = {}          # Tabla de conversión de caracteres
despl_ini        = 0           # Desplazamiento inicial para cargar desde memoria
fin_cadena       = ord ('\n')  # Carácter de fin de cadena
nueva_linea      = ord ('\r')  # Carácter de nueva línea
num_abreviaturas = 128         # Número de abreviaturas cuando se comprime el texto

# Desplazamientos iniciales para cargar desde memoria, de las plataformas en las que éste no es 0
despl_ini_plat = {
}
plats_LE = (2, )  # Plataformas que son Little Endian (PC)


# Diccionario de condactos

condactos = {
  # El formato es el siguiente:
  # código : (nombre, parámetros, es_acción, flujo)
  # Donde:
  #   parámetros es una cadena con el tipo de cada parámetro
  #   flujo indica si el condacto cambia el flujo de ejecución incondicionalmente, por lo que todo código posterior en su entrada será inalcanzable
  # Y los tipos de los parámetros se definen así:
  # % : Porcentaje (percent), de 1 a 99 (TODO: comprobar si sirven 0 y 100)
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
   18 : ('INVEN',   '',   True,  True),
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
   29 : ('CLS',     '',   True,  False),
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
   61 : ('EXTERN',  'u',  True,  False),
   62 : ('RAMSAVE', '',   True,  False),
   63 : ('RAMLOAD', 'f',  True,  False),
   64 : ('BELL',    '',   True,  False),   # O BEEP, según la plataforma que sea
   65 : ('PAPER',   'u',  True,  False),
   66 : ('INK',     'u',  True,  False),
   67 : ('BORDER',  'u',  True,  False),
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
   78 : ('CHARSET', 'u',  True,  False),
   79 : ('NOTEQ',   'fu', False, False),
   80 : ('NOTSAME', 'ff', False, False),
   81 : ('MODE',    'u',  True,  False),
   82 : ('LINE',    'u',  True,  False),
   83 : ('TIME',    'uu', True,  False),
   84 : ('PICTURE', 'l',  True,  False),
   85 : ('DOALL',   'L',  True,  False),
   86 : ('PROMPT',  's',  True,  False),
   87 : ('GRAPHIC', 'u',  True,  False),
   88 : ('ISNOTAT', 'oL', False, False),
   89 : ('WEIGH',   'of', True,  False),
   90 : ('PUTIN',   'ol', True,  False),
   91 : ('TAKEOUT', 'ol', True,  False),
   92 : ('NEWTEXT', '',   True,  False),
   93 : ('ABILITY', 'uu', True,  False),
   94 : ('WEIGHT',  'f',  True,  False),
   95 : ('RANDOM',  'f',  True,  False),
   96 : ('INPUT',   'u',  True,  False),
   97 : ('SAVEAT',  '',   True,  False),
   98 : ('BACKAT',  '',   True,  False),
   99 : ('PRINTAT', 'uu', True,  False),
  100 : ('WHATO',   '',   True,  False),
  101 : ('RESET',   'l',  True,  True),
  102 : ('PUTO',    'L',  True,  False),
  103 : ('NOTDONE', '',   True,  True),
  104 : ('AUTOP',   'l',  True,  False),
  105 : ('AUTOT',   'l',  True,  False),
  106 : ('MOVE',    'f',  False, False),  # Se comporta como condición
  107 : ('PROTECT', '',   True,  False),
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
  preparaPosCabecera ('pdb')
  return cargaBD (fichero, longitud)

# Carga la base de datos entera desde un fichero de imagen de memoria de Spectrum 48K
# Para compatibilidad con el IDE:
# - Recibe como primer parámetro un fichero abierto
# - Recibe como segundo parámetro la longitud del fichero abierto
# - Devuelve False si ha ocurrido algún error
def carga_bd_sna (fichero, longitud):
  if longitud != 49179:
    return False  # No parece un fichero de imagen de memoria de Spectrum 48K
  # Detectamos la posición de la cabecera de la base de datos
  posicion = 0
  fichero.seek (posicion)
  encajeSec = []
  secuencia = (16, None, 17, None, 18, None, 19, None, 20, None, 21)
  c = fichero.read (1)
  while c:
    if secuencia[len (encajeSec)] == None or ord (c) == secuencia[len (encajeSec)]:
      encajeSec.append (c)
      if len (encajeSec) == len (secuencia):
        break
    elif encajeSec:
      del encajeSec[:]
      continue  # Empezamos de nuevo desde este caracter
    c = fichero.read (1)
    posicion += 1
  else:
    return False  # Cabecera de la base de datos no encontrada
  preparaPosCabecera ('sna48k', posicion)
  return cargaBD (fichero, longitud)

def carga_sce (fichero, longitud):
  """Carga la base de datos desde el código fuente SCE del fichero de entrada

  Para compatibilidad con el IDE:
  - Recibe como primer parámetro un fichero abierto
  - Recibe como segundo parámetro la longitud del fichero abierto
  - Devuelve False si ha ocurrido algún error"""
  global plataforma, version
  # Los dos valores siguientes son necesarios para el intérprete y esta librería, pondremos valores de PAWS PC
  plataforma = 2
  version    = 1
  return alto_nivel.carga_sce (fichero, longitud, LONGITUD_PAL, atributos, [], condactos, {}, conexiones, desc_locs, desc_objs, locs_iniciales, msgs_usr, msgs_sys, nombres_objs, [], num_objetos, tablas_proceso, vocabulario)

def escribe_secs_ctrl (cadena):
  """Devuelve la cadena dada convirtiendo la representación de secuencias de control en sus códigos"""
  convertida = ''
  i = 0
  while i < len (cadena):
    c = cadena[i]
    o = ord (c)
    if c == '\t':
      convertida += '\x06'  # Tabulador
    else:
      convertida += c
    i += 1
  # TODO: interpretar las secuencias escapadas con barra invertida (\)
  return convertida

def inicializa_banderas (banderas):
  """Inicializa banderas con valores propios de PAWS"""
  # Bandera 39:
  # En todas las que he probado de ZX Spectrum, el intérprete la inicializa a 24
  if plataforma == 0 and version == 21:  # Formato sna de Spectrum 48K
    banderas[39] = 24

def lee_secs_ctrl (cadena):
  """Devuelve la cadena dada convirtiendo las secuencias de control en una representación imprimible"""
  convertida = ''
  i = 0
  while i < len (cadena):
    c = cadena[i]
    o = ord (c)
    if c == '\n':
      convertida += '\\n'
    elif c == '\x06':  # Tabulador
      convertida += '\\t'
    elif o in range (16, 21) and (i + 1) < len (cadena):
      convertida += '\\'
      if o == 16:
        convertida += 'TINTA'
      elif o == 17:
        convertida += 'PAPEL'
      elif o == 18:
        convertida += 'FLASH'
      elif o == 19:
        convertida += 'BRILLO'
      else:  # o == 20
        convertida += 'INVERSA'
      convertida += '_%02X' % ord (cadena[i + 1])
      i += 1  # El siguiente carácter ya se ha procesado
    elif c == '\\':
      convertida += '\\\\'
    else:
      convertida += c
    i += 1
  return convertida


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
  for i in range (num_abreviaturas):
    abreviatura = []
    seguir      = True
    while seguir:
      caracter = carga_int1()
      if caracter > 127:
        caracter -= 128
        seguir    = False
      if chr (caracter) in conversion:
        abreviatura.append (conversion[chr (caracter)])
      else:
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
  inicioAbrevs   = 255 - num_abreviaturas  # Primer código de carácter que es abreviatura
  saltaSiguiente = False                   # Si salta el siguiente carácter, como ocurre tras algunos códigos de control
  for posicion in posiciones:
    fich_ent.seek (posicion)
    cadena = []
    while True:
      caracter = carga_int1() ^ 255
      if caracter == fin_cadena:  # Fin de esta cadena
        break
      if (caracter >= inicioAbrevs) and abreviaturas:
        try:
          cadena.append (abreviaturas[caracter - inicioAbrevs])
        except:
          prn (caracter)
          raise
      elif saltaSiguiente or (version == 21 and caracter in (range (16, 21))):  # Códigos de control
        cadena.append (chr (caracter))
        saltaSiguiente = not saltaSiguiente
      elif caracter == nueva_linea:
        cadena.append ('\n')
      elif chr (caracter) in conversion:
        cadena.append (conversion[chr (caracter)])
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
    palabra   = [chr (caracter)]
    for i in range (4):
      caracter = carga_int1() ^ 255
      palabra.append (chr (caracter))
    # PAWS guarda las palabras de menos de cinco letras con espacios al final
    # PAWS guarda las palabras en mayúsculas
    vocabulario.append ((''.join (palabra).rstrip().lower(), carga_int1(), carga_int1()))

# Prepara la configuración sobre la plataforma
def preparaPlataforma ():
  global carga_int2, conversion, despl_ini, fin_cadena, guarda_int2, nueva_linea, num_abreviaturas, plataforma, version
  # Cargamos la versión del formato de base de datos y el identificador de plataforma
  fich_ent.seek (CAB_VERSION)
  version = carga_int1()
  # fich_ent.seek (CAB_PLATAFORMA)  # Son consecutivos
  plataforma = carga_int1()
  # Detectamos "endianismo"
  if plataforma in plats_LE or version == 21:  # Si el byte de versión vale 21, es formato sna
    carga_int2 = carga_int2_le
    bajo_nivel_cambia_endian (le = True)
  else:
    carga_int2 = carga_int2_be
    bajo_nivel_cambia_endian (le = False)
  # Preparamos el desplazamiento inicial para carga desde memoria
  if plataforma == 0 and version == 21:  # Formato sna de Spectrum 48K
    conversionPorDefecto = {'#': 'é', '$': 'í', '%': 'ó', '&': 'ú', '@': 'á', '[': '¡', ']': '¿', '^': '»', '`': '«', '|': 'ñ', '\x7f': '©', '\x80': ' ', '\x90': 'X', '\x92': u'\u2192', '\x93': u'\u2190', '\x97': '%'}
    conversionPorDefecto.update (conversion)
    conversion.update (conversionPorDefecto)
    despl_ini        = 16357
    fin_cadena       = 31
    nueva_linea      = 7
    num_abreviaturas = 91
    condactos[64]    = ('BEEP', 'uu', True, False)
    condactos[81]    = ('MODE', 'uu', True, False)
  elif plataforma in despl_ini_plat:
    despl_ini = despl_ini_plat[plataforma]
  bajo_nivel_cambia_despl (despl_ini)


# Funciones auxiliares que sólo se usan en este módulo

# Carga la base de datos entera desde el fichero de entrada
# Para compatibilidad con el IDE:
# - Recibe como primer parámetro un fichero abierto
# - Recibe como segundo parámetro la longitud del fichero abierto
# - Devuelve False si ha ocurrido algún error
def cargaBD (fichero, longitud):
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

# Asigna las "constantes" de desplazamientos (offsets/posiciones) en la cabecera
def preparaPosCabecera (formato, inicio = 0):
  global CAB_VERSION, CAB_PLATAFORMA, CAB_NUM_OBJS, CAB_NUM_LOCS, CAB_NUM_MSGS_USR, CAB_NUM_MSGS_SYS, CAB_NUM_PROCS, CAB_POS_ABREVS, CAB_POS_LST_POS_PROCS, CAB_POS_LST_POS_OBJS, CAB_POS_LST_POS_LOCS, CAB_POS_LST_POS_MSGS_USR, CAB_POS_LST_POS_MSGS_SYS, CAB_POS_LST_POS_CNXS, CAB_POS_VOCAB, CAB_POS_LOCS_OBJS, CAB_POS_NOMS_OBJS, CAB_POS_ATRIBS_OBJS, CAB_LONG_FICH
  CAB_VERSION      = inicio + 0  # Versión del formato de base de datos
  CAB_PLATAFORMA   = inicio + 1  # Identificador de plataforma e idioma
  CAB_NUM_OBJS     = inicio + 3  # Número de objetos
  CAB_NUM_LOCS     = inicio + 4  # Número de localidades
  CAB_NUM_MSGS_USR = inicio + 5  # Número de mensajes de usuario
  CAB_NUM_MSGS_SYS = inicio + 6  # Número de mensajes de sistema
  CAB_NUM_PROCS    = inicio + 7  # Número de procesos
  if formato == 'pdb':
    CAB_POS_ABREVS           =  8  # Posición de las abreviaturas
    CAB_POS_LST_POS_PROCS    = 10  # Posición lista de posiciones de procesos
    CAB_POS_LST_POS_OBJS     = 12  # Posición lista de posiciones de objetos
    CAB_POS_LST_POS_LOCS     = 14  # Posición lista de posiciones de localidades
    CAB_POS_LST_POS_MSGS_USR = 16  # Pos. lista de posiciones de mensajes de usuario
    CAB_POS_LST_POS_MSGS_SYS = 18  # Pos. lista de posiciones de mensajes de sistema
    CAB_POS_LST_POS_CNXS     = 20  # Posición lista de posiciones de conexiones
    CAB_POS_VOCAB            = 22  # Posición del vocabulario
    CAB_POS_LOCS_OBJS        = 24  # Posición de localidades iniciales de objetos
    CAB_POS_NOMS_OBJS        = 26  # Posición de los nombres de los objetos
    CAB_POS_ATRIBS_OBJS      = 28  # Posición de los atributos de los objetos
    CAB_LONG_FICH            = 30  # Longitud de la base de datos
  elif formato == 'sna48k':
    CAB_POS_ABREVS           = inicio + 11  # Posición de las abreviaturas
    CAB_POS_LST_POS_PROCS    = 49140        # Posición lista de posiciones de procesos
    CAB_POS_LST_POS_OBJS     = 49142        # Posición lista de posiciones de objetos
    CAB_POS_LST_POS_LOCS     = 49144        # Posición lista de posiciones de localidades
    CAB_POS_LST_POS_MSGS_USR = 49146        # Pos. lista de posiciones de mensajes de usuario
    CAB_POS_LST_POS_MSGS_SYS = 49148        # Pos. lista de posiciones de mensajes de sistema
    CAB_POS_LST_POS_CNXS     = 49150        # Posición lista de posiciones de conexiones
    CAB_POS_VOCAB            = 49152        # Posición del vocabulario
    CAB_POS_LOCS_OBJS        = 49154        # Posición de localidades iniciales de objetos
    CAB_POS_NOMS_OBJS        = 49156        # Posición de los nombres de los objetos
    CAB_POS_ATRIBS_OBJS      = 49158        # Posición de los atributos de los objetos
    CAB_LONG_FICH            = 49160        # Posición del siguiente byte tras la base de datos
