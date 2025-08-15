# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Librer�a de PAWS (parte com�n a editor, compilador e int�rprete)
# Copyright (C) 2020-2025 Jos� Manuel Ferrer Ortiz
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

from bajo_nivel      import *
from graficos_bitmap import carga_udgs_zx
from prn_func        import _, prn

import sys  # Para stderr

import alto_nivel


# Variables que se exportan (fuera del paquete)

# Ponemos los m�dulos de condactos en orden, para permitir que las funciones de los condactos de igual firma (nombre, tipo y n�mero de par�metros) de los sistemas m�s nuevos tengan precedencia sobre las de sistemas anteriores
mods_condactos = ('condactos_paws', 'condactos_quill')

atributos      = []   # Atributos de los objetos
colores_inicio = []   # Colores iniciales: tinta, papel, borde y opcionalmente brillo
conexiones     = []   # Listas de conexiones de cada localidad
desc_locs      = []   # Descripciones de las localidades
desc_objs      = []   # Descripciones de los objetos
locs_iniciales = []   # Localidades iniciales de los objetos
msgs_sys       = []   # Mensajes de sistema
msgs_usr       = []   # Mensajes de usuario
nombres_objs   = []   # Nombre y adjetivo de los objetos
num_objetos    = [0]  # N�mero de objetos (en lista para pasar por referencia)
pos_fuentes    = []   # Posiciones de las fuentes tipogr�ficas
tablas_proceso = []   # Tablas de proceso
udgs           = []   # UDGs (caracteres gr�ficos definidos por el usuario)
vocabulario    = []   # Vocabulario

# Funciones que importan bases de datos desde ficheros
funcs_exportar = ()  # Ninguna, de momento
funcs_importar = (
  ('carga_bd',     ('pdb',), _('PAWS databases')),
  ('carga_bd_sna', ('sna',), _('ZX 48K memory snapshots with PAWS')),
  ('carga_sce',    ('sce',), _('PAWS source code')),
)
# Funci�n que crea una nueva base de datos (vac�a)
func_nueva = ''


# Constantes que se exportan (fuera del paquete)

EXT_SAVEGAME     = 'pgp'   # Extensi�n para las partidas guardadas
INDIRECCION      = False   # El parser no soporta indirecci�n (para el IDE)
LONGITUD_PAL     = 5       # Longitud m�xima para las palabras de vocabulario
NOMBRE_SISTEMA   = 'PAWS'  # Nombre de este sistema
NUM_ATRIBUTOS    = [2]     # N�mero de atributos de objeto
NUM_BANDERAS     = [256]   # N�mero de banderas del parser
NUM_BANDERAS_ACC = [256]   # N�mero de banderas del parser accesibles por el programador
NOMB_COMO_VERB   = [20]    # N�mero de nombres convertibles a verbo
PREP_COMO_VERB   = 0       # N�mero de preposiciones convertibles a verbo
# Nombres de las primeras tablas de proceso (para el IDE)
NOMBRES_PROCS    = (_('Response table'), _('After description'), _('Each turn'))
# Nombres de los tipos de palabra (para el IDE y el int�rprete)
TIPOS_PAL    = (_('Verb'), _('Adverb'), _('Noun'), _('Adjective'), _('Preposition'), _('Conjugation'), _('Pronoun'))
TIPOS_PAL_ES = ('Verbo', 'Adverbio', 'Nombre', 'Adjetivo', 'Preposicion', 'Conjuncion', 'Pronombre')


alinear          = False       # Si alineamos con relleno (padding) las listas de desplazamientos a posiciones pares
compatibilidad   = True        # Modo de compatibilidad con los int�rpretes originales
conversion       = {}          # Tabla de conversi�n de caracteres
despl_ini        = 0           # Desplazamiento inicial para cargar desde memoria
fin_cadena       = ord ('\n')  # Car�cter de fin de cadena
id_plataforma    = ''          # Identificador de plataforma como cadena
nueva_linea      = ord ('\r')  # Car�cter de nueva l�nea
num_abreviaturas = 129         # N�mero de abreviaturas cuando se comprime el texto

# Desplazamientos iniciales para cargar desde memoria, de las plataformas en las que �ste no es 0
despl_ini_plat = {
  0: 16357,  # ZX Spectrum
  1: 6400,   # Amstrad CPC
}
plats_LE = (1, 2)  # Plataformas que son Little Endian (Amstrad CPC y PC)


# Diccionario de condactos

condactos = {
  # El formato es el siguiente:
  # c�digo : (nombre, par�metros, es_acci�n, flujo)
  # Donde:
  #   par�metros es una cadena con el tipo de cada par�metro
  #   flujo indica si el condacto cambia el flujo de ejecuci�n incondicionalmente, por lo que todo c�digo posterior en su entrada ser� inalcanzable
  # Y los tipos de los par�metros se definen as�:
  # % : Porcentaje (percent), de 1 a 99 (TODO: comprobar si sirven 0 y 100)
  # f : N�mero de bandera (flagno), de 0 a NUM_BANDERAS - 1
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
   20 : ('QUIT',    '',   False, False),  # Se comporta como condici�n, no satisfecha si no termina
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
   46 : ('PLACE',   'oL', True,  False),  # TODO: investigar m�s si en alg�n caso se comporta como condici�n
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
   64 : ('BELL',    '',   True,  False),   # O BEEP, seg�n la plataforma que sea
   65 : ('PAPER',   'u',  True,  False),
   66 : ('INK',     'u',  True,  False),
   67 : ('BORDER',  'u',  True,  False),
   68 : ('PREP',    'r',  False, False),
   69 : ('NOUN2',   'n',  False, False),
   70 : ('ADJECT2', 'j',  False, False),
   71 : ('ADD',     'ff', True,  False),
   72 : ('SUB',     'ff', True,  False),
   73 : ('PARSE',   '',   False, False),  # Se comporta como condici�n, satisfecha con frase inv�lida
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
  106 : ('MOVE',    'f',  False, False),  # Se comporta como condici�n
  107 : ('PROTECT', '',   True,  False),
}


# Funciones que utiliza el IDE o el int�rprete directamente

def cadena_es_mayor (cadena1, cadena2):
  """Devuelve si la cadena1 es mayor a la cadena2 en el juego de caracteres de este sistema"""
  return cadena1 > cadena2

def carga_bd (fichero, longitud):
  """"Carga la base de datos entera desde un fichero de base de datos PDB de PAWS PC

Para compatibilidad con el IDE:
- Recibe como primer par�metro un fichero abierto
- Recibe como segundo par�metro la longitud del fichero abierto
- Devuelve False si ha ocurrido alg�n error"""
  global id_plataforma
  id_plataforma = 'PC'
  preparaPosCabecera ('pdb')
  return cargaBD (fichero, longitud)

def carga_bd_sna (fichero, longitud):
  """Carga la base de datos entera desde un fichero de imagen de memoria de Spectrum 48K

Para compatibilidad con el IDE:
- Recibe como primer par�metro un fichero abierto
- Recibe como segundo par�metro la longitud del fichero abierto
- Devuelve False si ha ocurrido alg�n error"""
  global id_plataforma
  if longitud != 49179:
    return False  # No parece un fichero de imagen de memoria de Spectrum 48K
  id_plataforma = 'ZX'
  # Detectamos la posici�n de la cabecera de la base de datos
  bajo_nivel_cambia_ent (fichero)
  posicion = busca_secuencia ((16, None, 17, None, 18, None, 19, None, 20, None, 21))
  if posicion == None:
    return False  # Cabecera de la base de datos no encontrada
  # Cargamos los colores iniciales
  fichero.seek (posicion - 9)
  colores_inicio.append (ord (fichero.read (1)))  # Color de tinta
  fichero.read (1)
  colores_inicio.append (ord (fichero.read (1)))  # Color de papel
  fichero.read (3)
  colores_inicio.append (ord (fichero.read (1)))  # Brillo
  fichero.read (5)
  colores_inicio.insert (2, ord (fichero.read (1)))  # Color de borde
  preparaPosCabecera ('sna48k', posicion)
  del udgs[:]
  udgs.extend (carga_udgs_zx (fichero, posicion - 321, 19)[0])
  return cargaBD (fichero, longitud)

def carga_sce (fichero, longitud):
  """Carga la base de datos desde el c�digo fuente SCE del fichero de entrada

  Para compatibilidad con el IDE:
  - Recibe como primer par�metro un fichero abierto
  - Recibe como segundo par�metro la longitud del fichero abierto
  - Devuelve False si ha ocurrido alg�n error"""
  global id_plataforma, plataforma, version
  # Los dos valores siguientes son necesarios para el int�rprete y esta librer�a, pondremos valores de PAWS PC
  plataforma = 2  # TODO: asignar valor 1 cuando se detecte que es Amstrad CPC (indica letra de unidad en secci�n /CTL)
  version    = 1
  id_plataforma = 'PC'
  retorno = alto_nivel.carga_codigo_fuente (fichero, longitud, LONGITUD_PAL, atributos, [], condactos, {}, conexiones, desc_locs, desc_objs, locs_iniciales, msgs_usr, msgs_sys, nombres_objs, [], num_objetos, tablas_proceso, vocabulario, escribe_secs_ctrl)
  # Liberamos la memoria utilizada para la carga
  import gc
  gc.collect()
  return retorno

def inicializa_banderas (banderas):
  """Inicializa banderas con valores propios de PAWS"""
  # Bandera 39:
  # En todas las que he probado de ZX Spectrum, el int�rprete la inicializa a 24
  if plataforma == 0 and version == 21:  # Formato sna de Spectrum 48K
    banderas[39] = 24

def escribe_secs_ctrl (cadena):
  """Devuelve la cadena dada convirtiendo la representaci�n de secuencias de control en sus c�digos"""
  convertida = ''
  i = 0
  while i < len (cadena):
    c = cadena[i]
    o = ord (c)
    if c == '\t':
      convertida += '\x06'  # Tabulador
    elif c == '\\':
      if cadena[i + 1:i + len(_('TAB')) + 2] == _('TAB') + '_':
        columna = cadena[i + len(_('TAB')) + 2:i + len(_('TAB')) + 4]
        try:
          columna     = int (columna, 16)
          convertida += chr (23) + chr (columna)
        except:
          pass
        i += len (_('TAB')) + 3
      elif cadena[i + 1:i + 2] == 'x':  # C�digos escritos en hexadecimal
        try:
          codigo = int (cadena[i + 2: i + 4], 16)
        except:
          codigo = 0
        convertida += chr (codigo)
        i += 3
      else:
        convertida += c
      # TODO: interpretar el resto de secuencias escapadas con barra invertida (\)
    else:
      convertida += c
    i += 1
  # TODO: interpretar las secuencias escapadas con barra invertida (\)
  return convertida

def lee_secs_ctrl (cadena):
  """Devuelve la cadena dada convirtiendo las secuencias de control en una representaci�n imprimible"""
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
        convertida += _('INK')
      elif o == 17:
        convertida += _('PAPER')
      elif o == 18:
        convertida += _('FLASH')
      elif o == 19:
        convertida += _('BRIGHT')
      else:  # o == 20
        convertida += _('INVERSE')
      convertida += '_%02X' % ord (cadena[i + 1])
      i += 1  # El siguiente car�cter ya se ha procesado
    elif o == 23:
      convertida += '\\' + _('TAB') + '_%02X' % ord (cadena[i + 1])
      i += 2  # El siguiente car�cter ya se ha procesado y el de despu�s se ignora
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
  # Vamos a la posici�n de las abreviaturas
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
    #prn (i, ' |', abreviaturas[-1], '|', sep = '', file = sys.stderr)

# Carga los atributos de los objetos
def cargaAtributos ():
  # Cargamos el n�mero de objetos (no lo tenemos todav�a)
  fich_ent.seek (CAB_NUM_OBJS)
  num_objetos[0] = carga_int1()
  # Vamos a la posici�n de los atributos de los objetos
  fich_ent.seek (carga_desplazamiento (CAB_POS_ATRIBS_OBJS))
  # Cargamos los atributos de cada objeto
  for i in range (num_objetos[0]):
    atributos.append (carga_int1())

# Carga un conjunto gen�rico de cadenas
# pos_num_cads es la posici�n de donde obtener el n�mero de cadenas
# pos_lista_pos posici�n de donde obtener la lista de posiciones de las cadenas
# cadenas es la lista donde almacenar las cadenas que se carguen
def cargaCadenas (pos_num_cads, pos_lista_pos, cadenas):
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
  inicioAbrevs   = 255 - num_abreviaturas  # Primer c�digo de car�cter que es abreviatura
  inicioAbrevs   = max(inicioAbrevs, 127)  # La abreviatura #0 (c�digo 126) nunca se reemplaza cuando hay 129 abreviaturas
  saltaSiguiente = False                   # Si salta el siguiente car�cter, como ocurre tras algunos c�digos de control
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
      elif saltaSiguiente or (version == 21 and caracter in (range (16, 21))):  # C�digos de control
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

# Carga las tablas de procesos
# El proceso 0 es la tabla de respuestas
# En los procesos 1 y 2, las cabeceras de las entradas se ignoran
def cargaTablasProcesos ():
  # Cargamos el n�mero de procesos
  fich_ent.seek (CAB_NUM_PROCS)
  num_procs = carga_int1()
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
        num_condacto = condacto
        parametros = []
        if num_condacto not in condactos:
          try:
            muestraFallo ('FIXME: Condacto desconocido', 'C�digo de condacto: ' + str (num_condacto) + '\nProceso: ' + str (num_proceso) + '\n�ndice de entrada: ' + str (num_entrada))
          except:
            prn ('FIXME: N�mero de condacto', num_condacto, 'desconocido, en entrada', num_entrada, 'del proceso', num_proceso, file = sys.stderr)
          return
        for i in range (len (condactos[num_condacto][1])):
          parametros.append (carga_int1())
        entrada.append ((condacto, parametros))
      entradas.append (entrada)
    if len (cabeceras) != len (entradas):
      prn ('ERROR: N�mero distinto de cabeceras y entradas para una tabla de procesos', file = sys.stderr)
      return
    tablas_proceso.append ((cabeceras, entradas))

# Carga el vocabulario
def cargaVocabulario ():
  # Vamos a la posici�n del vocabulario
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
    # PAWS guarda las palabras en may�sculas
    vocabulario.append ((''.join (palabra).rstrip().lower(), carga_int1(), carga_int1()))

# Prepara la configuraci�n sobre la plataforma
def preparaPlataforma ():
  global carga_desplazamiento, carga_int2, conversion, despl_ini, fin_cadena, guarda_int2, nueva_linea, num_abreviaturas, plataforma, version
  carga_desplazamiento = carga_desplazamiento2
  # Cargamos la versi�n del formato de base de datos y el identificador de plataforma
  fich_ent.seek (CAB_VERSION)
  version = carga_int1()
  # fich_ent.seek (CAB_PLATAFORMA)  # Son consecutivos
  plataforma = carga_int1()
  # Detectamos "endianismo"
  if plataforma in plats_LE or version == 21:  # Si el byte de versi�n vale 21, es formato sna
    carga_int2 = carga_int2_le
    bajo_nivel_cambia_endian (le = True)
  else:
    carga_int2 = carga_int2_be
    bajo_nivel_cambia_endian (le = False)
  # Preparamos el desplazamiento inicial para carga desde memoria
  if plataforma == 0 and version == 21:  # Formato sna de Spectrum 48K
    # Evitamos conversi�n de caracteres por defecto para Spectrum ZX cuando hay GUI gr�fica, para que imprima lo que corresponda a la fuente tipogr�fica y UDGs
    if 'NOMBRE_GUI' not in globals() or NOMBRE_GUI != 'pygame':
      conversionPorDefecto = {'#': '�', '$': '�', '%': '�', '&': '�', '@': '�', '[': '�', ']': '�', '^': '�', '`': '�', '|': '�', '\x7f': '�', '\x80': ' ', '\x90': 'X', '\x92': u'\u2192', '\x93': u'\u2190', '\x97': '%'}
      conversionPorDefecto.update (conversion)
      conversion.update (conversionPorDefecto)
    fin_cadena       = 31
    nueva_linea      = 7
    num_abreviaturas = 91
    condactos[64]    = ('BEEP', 'uu', True, False)
    condactos[81]    = ('MODE', 'uu', True, False)
  if plataforma in despl_ini_plat:
    despl_ini = despl_ini_plat[plataforma]
  bajo_nivel_cambia_despl (despl_ini)


# Funciones auxiliares que s�lo se usan en este m�dulo

# Carga la base de datos entera desde el fichero de entrada
# Para compatibilidad con el IDE:
# - Recibe como primer par�metro un fichero abierto
# - Recibe como segundo par�metro la longitud del fichero abierto
# - Devuelve False si ha ocurrido alg�n error
def cargaBD (fichero, longitud):
  global fich_ent, long_fich_ent  # Fichero de entrada y su longitud
  fich_ent      = fichero
  long_fich_ent = longitud
  bajo_nivel_cambia_ent (fichero)
  try:
    preparaPlataforma()
    if 'CAB_NUM_FUENTES' in globals():
      numFuentes = carga_int1 (CAB_NUM_FUENTES)
      posFuentes = carga_desplazamiento (CAB_POS_FUENTES)
      for f in range (numFuentes):
        pos_fuentes.append (posFuentes + f * 768)
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
  global CAB_VERSION, CAB_PLATAFORMA, CAB_NUM_OBJS, CAB_NUM_LOCS, CAB_NUM_MSGS_USR, CAB_NUM_MSGS_SYS, CAB_NUM_PROCS, CAB_NUM_FUENTES, CAB_POS_FUENTES, CAB_POS_ABREVS, CAB_POS_LST_POS_PROCS, CAB_POS_LST_POS_OBJS, CAB_POS_LST_POS_LOCS, CAB_POS_LST_POS_MSGS_USR, CAB_POS_LST_POS_MSGS_SYS, CAB_POS_LST_POS_CNXS, CAB_POS_VOCAB, CAB_POS_LOCS_OBJS, CAB_POS_NOMS_OBJS, CAB_POS_ATRIBS_OBJS, CAB_LONG_FICH
  CAB_VERSION      = inicio + 0  # Versi�n del formato de base de datos
  CAB_PLATAFORMA   = inicio + 1  # Identificador de plataforma e idioma
  CAB_NUM_OBJS     = inicio + 3  # N�mero de objetos
  CAB_NUM_LOCS     = inicio + 4  # N�mero de localidades
  CAB_NUM_MSGS_USR = inicio + 5  # N�mero de mensajes de usuario
  CAB_NUM_MSGS_SYS = inicio + 6  # N�mero de mensajes de sistema
  CAB_NUM_PROCS    = inicio + 7  # N�mero de procesos
  if formato == 'pdb':
    CAB_POS_ABREVS           =  8  # Posici�n de las abreviaturas
    CAB_POS_LST_POS_PROCS    = 10  # Posici�n lista de posiciones de procesos
    CAB_POS_LST_POS_OBJS     = 12  # Posici�n lista de posiciones de objetos
    CAB_POS_LST_POS_LOCS     = 14  # Posici�n lista de posiciones de localidades
    CAB_POS_LST_POS_MSGS_USR = 16  # Pos. lista de posiciones de mensajes de usuario
    CAB_POS_LST_POS_MSGS_SYS = 18  # Pos. lista de posiciones de mensajes de sistema
    CAB_POS_LST_POS_CNXS     = 20  # Posici�n lista de posiciones de conexiones
    CAB_POS_VOCAB            = 22  # Posici�n del vocabulario
    CAB_POS_LOCS_OBJS        = 24  # Posici�n de localidades iniciales de objetos
    CAB_POS_NOMS_OBJS        = 26  # Posici�n de los nombres de los objetos
    CAB_POS_ATRIBS_OBJS      = 28  # Posici�n de los atributos de los objetos
    CAB_LONG_FICH            = 30  # Longitud de la base de datos
  elif formato == 'sna48k':
    CAB_NUM_FUENTES          = inicio + 8   # N�mero de fuentes tipogr�ficas
    CAB_POS_FUENTES          = inicio + 9   # Posici�n de las fuentes tipogr�ficas
    CAB_POS_ABREVS           = inicio + 11  # Posici�n de las abreviaturas
    CAB_POS_LST_POS_PROCS    = 49140        # Posici�n lista de posiciones de procesos
    CAB_POS_LST_POS_OBJS     = 49142        # Posici�n lista de posiciones de objetos
    CAB_POS_LST_POS_LOCS     = 49144        # Posici�n lista de posiciones de localidades
    CAB_POS_LST_POS_MSGS_USR = 49146        # Pos. lista de posiciones de mensajes de usuario
    CAB_POS_LST_POS_MSGS_SYS = 49148        # Pos. lista de posiciones de mensajes de sistema
    CAB_POS_LST_POS_CNXS     = 49150        # Posici�n lista de posiciones de conexiones
    CAB_POS_VOCAB            = 49152        # Posici�n del vocabulario
    CAB_POS_LOCS_OBJS        = 49154        # Posici�n de localidades iniciales de objetos
    CAB_POS_NOMS_OBJS        = 49156        # Posici�n de los nombres de los objetos
    CAB_POS_ATRIBS_OBJS      = 49158        # Posici�n de los atributos de los objetos
    CAB_LONG_FICH            = 49160        # Posici�n del siguiente byte tras la base de datos
